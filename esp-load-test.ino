#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>

const char *ssid = "ESP8266";
const char *password = "pass";

const int bufSize = 1000; // Transfer buffer size in bytes

WiFiServer server(80);    // Server port

void setup()
{
    Serial.begin(9600);

    // Connecting to WiFi as an station
    Serial.print("[WiFi] Connecting.");
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print('.');
    }

    Serial.println(' ');
    Serial.println("[WiFi] Connected to ssid: " + String(ssid));
    Serial.print("[WiFi] IP: ");
    Serial.println(WiFi.localIP());

    // Start the Multicast DNS server
    if (MDNS.begin("esp-8266"))
    {
        Serial.println("[MDNS] Serving: esp-8266.local");
    }

    server.begin();
    server.setNoDelay(true);
}

// Create the HTML page header 
String getHTMLHead()
{
    String htmlPage =
        String("HTTP/1.1 200 OK\r\n") +
        "Content-Type: application/octet-stream\r\n" +
        "Content-Length: 999999999999\r\n" +
        "Connection: close\r\n" +
        "\r\n";

    return htmlPage;
}

// Server connection loop
void loop()
{
    WiFiClient client = server.available();
    if (client && client.connected())
    {
        Serial.println("A client found!");
        String line = client.readStringUntil('\n');
        Serial.println(line);
        client.println(getHTMLHead());

        // Data sending loop
        while (client.status())
        {
            byte clientBuf[bufSize];
            client.write((const uint8_t *)clientBuf, bufSize);
        }
        Serial.println("Client stopped!");
    }
}