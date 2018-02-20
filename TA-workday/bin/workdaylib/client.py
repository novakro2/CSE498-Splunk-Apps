#!/usr/bin/env python

from __future__ import print_function

import re
import json
import time
import random

import requests


class Workday(object):

	# Maximum retries after an HTTP error for a single request
	MAX_RETRIES = 2

	# Match a correctly formatted REST API endpoint url in Workday
	REST_API_ENDPOINT_PATTERN = re.compile("^https://(?P<host>[^/:]+)(?::\d+)?/ccx/api/v1/(?P<tenant>[^/]+)$")

	# Match a correctly formatted OAuth2 Token endpoint url in Workday
	TOKEN_ENDPOINT_PATTERN = re.compile("^https://(?P<host>[^/:]+)(?::\d+)?/ccx/oauth2/(?P<tenant>[^/]+)/token$")

	# Match a FQDN that is owned by Workday and may host a valid tenant
	WORKDAY_HOSTNAME_PATTERN = re.compile("^.+\.(?:workday\.com|myworkday\.com|workdaysuv\.com|workday\.net)$")

	# Timeout for connecting to the API server (seconds)
	CONNECT_TIMEOUT = 5

	# Timeout for reading data from the API server, after the connection is made (seconds)
	READ_TIMEOUT = 60

	def __init__(self, rest_api_endpoint, token_endpoint, client_id, client_secret, refresh_token, http_user_agent=None, helper=None):
		"""
		Create a Workday service object using the provided API client credentials.

		Args:
			rest_api_endpoint: base url for the Workday REST API (tenanted)
			token_endpoint: url for the OAuth2 token authentication endpoint (tenanted)
			client_id: OAuth2 client id
			client_secret: OAuth2 client secret
			refresh_token: OAuth2 refresh token
			http_user_agent: custom User-Agent value to use for all requests
			helper: helper object provided by the Splunk Add-on Builder, used for logging internal actions

		Returns:
			New Workday service object

		Raises:
			ValueError: Raised when the provided credentials fail validation checks
		"""
		# API host details
		rest_api_endpoint = rest_api_endpoint.strip().rstrip("/")
		token_endpoint = token_endpoint.strip().rstrip("/")
		try:
			self._validate_urls(rest_api_endpoint, token_endpoint)
			self._api_base_url = rest_api_endpoint
			self._refresh_url = token_endpoint

			url_groups = self.REST_API_ENDPOINT_PATTERN.match(rest_api_endpoint).groupdict()
			self.host = url_groups["host"]
			self.tenant = url_groups["tenant"]
		except Exception as e:
			raise ValueError("Invalid URL endpoint provided: {}".format(str(e)))

		# API client credentials
		self._client_id = client_id.strip()
		self._client_secret = client_secret.strip()
		self._refresh_token = refresh_token.strip()

		self._session = requests.Session()
		if http_user_agent is not None:
			self._session.headers["User-Agent"] = http_user_agent

		self._helper = helper
		self._access_token = None

	@classmethod
	def _timestamp(cls, date_obj):
		return date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")

	def _validate_urls(self, rest_api_endpoint, token_endpoint):
		"""
		Validate that provided urls are correct and formatted as expected.

		Returns:
			None

		Raises:
			ValueError: any arguments fail validation
		"""

		# Validate urls since we are allowing users to enter them directly (the hostname is different between prod and impl,
		# and the tenant id will be different for every customer). Attempting to access an incorrect url may expose the client credentials.
		#
		# The exact urls needed can be copied from the "View API Clients" task in Workday

		# Check 1: Confirm expected url patterns
		match = self.REST_API_ENDPOINT_PATTERN.match(rest_api_endpoint)
		if not match:
			raise ValueError("REST API Endpoint must match the format \"https://<hostname>/ccx/api/v1/<tenant>\"")
		else:
			base_url_groups = match.groupdict()

		match = self.TOKEN_ENDPOINT_PATTERN.match(token_endpoint)
		if not match:
			raise ValueError("Token Endpoint must match the format \"https://<hostname>/ccx/oauth2/<tenant>/token\"")
		else:
			token_url_groups = match.groupdict()

		# Check 2: Confirm both urls are from the same environment / tenant
		if base_url_groups["host"] != token_url_groups["host"]:
			raise ValueError("REST API Endpoint and Token Endpoint hostnames do not match")
		if base_url_groups["tenant"] != token_url_groups["tenant"]:
			raise ValueError("REST API Endpoint and Token Endpoint tenant ids do not match")

		# Check 3: Confirm urls point to a Workday owned system
		if not self.WORKDAY_HOSTNAME_PATTERN.match(base_url_groups["host"]):
			raise ValueError("Provided endpoint url is not a Workday address, refusing to connect")

	def _refresh_access_token(self):
		"""
		Authenticate with the stored token_endpoint to retrieve a temporary OAuth2 access token for API requests.

		Returns:
			string containing the access token value

		Raises:
			requests.exceptions.*: any connection exception is raised immediately
			ValueError: successful response content does not contain expected data
		"""
		resp = self._session.post(
			self._refresh_url,
			auth = (self._client_id, self._client_secret),
			data = { "refresh_token": self._refresh_token, "grant_type": "refresh_token" },
			timeout = (self.CONNECT_TIMEOUT, self.READ_TIMEOUT)
		)
		resp.raise_for_status()
		data = resp.json()
		if "access_token" in data:
			self._access_token = data["access_token"]
			return self._access_token
		else:
			raise ValueError("'access_token' field not returned in successful response")

	def _get(self, endpoint, *args, **kwargs):
		"""
		Make HTTP GET request to the given url path with given params, handling error retries and authentication.

		Args:
			endpoint: url path for the request, relative to this clients api base url
			args: general positional arguments, passed directly to the request
			kwargs: general keyword arguments, passed directly to the request

		Returns:
			requests.Response

		Raises:
			requests.exceptions.HTTPError: reraise any HTTPError after self.MAX_RETRIES retries
			requests.exceptions.Timeout: reraise any Timeout after self.MAX_RETRIES retries
			requests.exceptions.*: any other exception in the request is raised immediately
		"""
		if self._access_token is None:
			self._refresh_access_token()
		if "headers" not in kwargs:
			kwargs["headers"] = {}
		if "timeout" not in kwargs:
			kwargs["timeout"] = (self.CONNECT_TIMEOUT, self.READ_TIMEOUT)
		kwargs["headers"]["Authorization"] = "Bearer {}".format(self._access_token)

		retry_count = 0
		while True:
			try:
				resp = self._session.get(self._api_base_url + endpoint, *args, **kwargs)
				resp.raise_for_status()

			except requests.exceptions.Timeout as e:
				# Timeout in HTTP request, retry
				if retry_count < self.MAX_RETRIES:
					retry_count += 1
					time.sleep(random.randint(1, 5))
					if self._helper:
						self._helper.log_warning("Request timed out, retrying (attempt {}/{})".format(retry_count, self.MAX_RETRIES))
					continue
				# Halt and escalate, retries exhausted
				else:
					raise

			except requests.exceptions.HTTPError as e:
				# HTTP error, retry
				if retry_count < self.MAX_RETRIES:
					retry_count += 1
					time.sleep(random.randint(1, 5))
					if e.response.status_code == 401:
						self._refresh_access_token()
					if self._helper:
						self._helper.log_warning("Request failed with error code ({}), retrying (attempt {}/{})".format(e.response.status_code, retry_count, self.MAX_RETRIES))
					continue
				# Halt and escalate, retries exhausted
				else:
					raise

			else:
				# Success
				return resp

	def audit_logs(self, start, end=None, include_target=False):
		"""
		Stream log events from the Workday auditLogs api within the time range (start, end).

		Args:
			start: start of query range, python datetime object
			end: end of query range, python datetime object
			include_target: pass True to include the target field in each log result, boolean

		Returns:
			python generator that streams log results from the query

		Raises:
			see _get
		"""
		endpoint = "/auditLogs"
		batch_size = 100

		if end is None:
			end = datetime.datetime.utcnow()

		start = self._timestamp(start)
		end   = self._timestamp(end)

		offset, total = 0, 1
		result_count = 0
		while result_count < total:
			resp = self._get(
				endpoint,
				headers = { "Content-Type": "application/json" },
				params = { "from": start, "to": end, "offset": offset, "limit": batch_size, "type": "userActivity" }
			)
			blob    = json.loads(resp.content)
			total   = int(blob["total"])
			offset += batch_size
			for result in blob["data"]:
				result["tenantId"] = self.tenant
				result["tenantHost"] = self.host
				# There's no current way to change query to exclude target, must download full logs and delete the target before storing
				if not include_target and "target" in result:
					del result["target"]
				result_count += 1
				yield result
