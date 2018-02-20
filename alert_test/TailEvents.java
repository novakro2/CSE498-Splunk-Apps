/**
 * This is a Java implementation of the tailevents.sh script.
 * As with tailevents.sh, assumes client.properties and referenceclient.jar are in the current directory.
 * To compile:
 *   javac TailEvents.java
 * To run:
 *   java TailEvents
 */

import java.io.FileInputStream;
import java.util.Properties;

public class TailEvents {
    // Full path of the client properties file
    public static final String DEFAULT_CLIENT_CONFIG_FILE = "client.properties";
    
    public static void main(String[] args) throws Exception {
        final String configFile = args.length > 0 ? args[0] : DEFAULT_CLIENT_CONFIG_FILE;
        System.out.println("Reading configuration from " + configFile);
        final Properties props = new Properties();
        try (FileInputStream input = new FileInputStream(configFile)) {
            props.load(input);
        }
        final String clientLogDir = props.getProperty("client_log_dir", "logs");
        System.out.println("Client logs will be written under the directory " + clientLogDir);

        final String eventLogDir = props.getProperty("event_log_dir", "logs");
        System.out.println("Event logs will be written under the directory " + eventLogDir);

        final String logLevel = props.getProperty("log_level", "INFO");
        System.out.println("Logging level of the client is set to " + logLevel);

        while (true) {
            System.out.println("Starting java process ...");
            int exitCode = new ProcessBuilder("java",
                "-Dclient_log_dir=" + clientLogDir,
                "-Devent_log_dir=" + eventLogDir,
                "-Dlog_level=" + logLevel,
                "-jar", "referenceclient.jar",
                "--spring.config.location=file:" + configFile
            ).inheritIO().start().waitFor();
            System.out.println("Java process exited with code " + exitCode + ". Will wait for 5 seconds and restart.");
            Thread.sleep(5000);
        }
    }
}
