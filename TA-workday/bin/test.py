#!/usr/bin/env python

import unittest

import requests

from workdaylib.client import Workday


dummy_rest_url = "https://test.workdaysuv.com/ccx/api/v1/example"
dummy_token_url = "https://test.workdaysuv.com/ccx/oauth2/example/token"
dummy_client_id = "xxx"
dummy_client_secret = "xxx"
dummy_refresh_token = "xxx"

class TestURLValidation(unittest.TestCase):

	def test_url_valid(self):
		try:
			for tld in ["workday.com", "myworkday.com", "workdaysuv.com", "workday.net"]:
				wday = Workday(
					"https://test.{tld}/ccx/api/v1/example".format(tld=tld),
					"https://test.{tld}/ccx/oauth2/example/token".format(tld=tld),
					dummy_client_id,
					dummy_client_secret,
					dummy_refresh_token
				)
		except Exception as e:
			self.fail("Client raised unexpected exception: " + str(e))

	def test_url_rest_api_invalid_pattern(self):
		bad_urls = [
			"www.example.com/ccx/api/v2/example",				# No scheme
			"http://www.example.com/ccx/api/v1/example",		# Not https
			"https://www.example.com/ccx/api/v2/example",		# Incorrect api version
			"https://www.example.com/ccx/api/v1/"				# Missing tenant id
			"https://www.example.com/api/v1/example",			# Incorrect url path
		]
		for url in bad_urls:
			with self.assertRaises(ValueError) as context:
				wday = Workday(url, dummy_token_url, dummy_client_id, dummy_client_secret, dummy_refresh_token)
			self.assertEqual(str(context.exception), "Invalid URL endpoint provided: REST API Endpoint must match the format \"https://<hostname>/ccx/api/v1/<tenant>\"")

	def test_url_token_invalid_pattern(self):
		rest_url = "https://www.example.com/ccx/api/v1/example"
		bad_urls = [
			"www.example.com/ccx/oauth2/example/token"			# No scheme
			"http://www.example.com/ccx/oauth2/example/token",	# Not https
			"https://www.example.com/oauth2/example/token",		# Incorrect url path
			"https://www.example.com/ccx/oauth2//token"			# Missing tenant id
		]
		for url in bad_urls:
			with self.assertRaises(ValueError) as context:
				wday = Workday(dummy_rest_url, url, dummy_client_id, dummy_client_secret, dummy_refresh_token)
			self.assertEqual(str(context.exception), "Invalid URL endpoint provided: Token Endpoint must match the format \"https://<hostname>/ccx/oauth2/<tenant>/token\"")

	def test_url_host_mismatch(self):
		with self.assertRaises(ValueError) as context:
			wday = Workday("https://www1.example.com/ccx/api/v1/example", "https://www2.example.com/ccx/oauth2/example/token", dummy_client_id, dummy_client_secret, dummy_refresh_token)
		self.assertEqual(str(context.exception), "Invalid URL endpoint provided: REST API Endpoint and Token Endpoint hostnames do not match")

	def test_url_tenant_mismatch(self):
		with self.assertRaises(ValueError) as context:
			wday = Workday("https://www.example.com/ccx/api/v1/example1", "https://www.example.com/ccx/oauth2/example2/token", dummy_client_id, dummy_client_secret, dummy_refresh_token)
		self.assertEqual(str(context.exception), "Invalid URL endpoint provided: REST API Endpoint and Token Endpoint tenant ids do not match")

	def test_url_non_workday_owned(self):
		with self.assertRaises(ValueError) as context:
			wday = Workday("https://www.example.com/ccx/api/v1/example", "https://www.example.com/ccx/oauth2/example/token", dummy_client_id, dummy_client_secret, dummy_refresh_token)
		self.assertEqual(str(context.exception), "Invalid URL endpoint provided: Provided endpoint url is not a Workday address, refusing to connect")



if __name__ == "__main__":
    unittest.main()
