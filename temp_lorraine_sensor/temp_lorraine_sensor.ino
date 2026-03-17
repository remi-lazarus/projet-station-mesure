#include <OneWire.h>
#include <DallasTemperature.h>
#include <WiFi.h>
#include <HTTPClient.h>

// GPIO where the DS18B20 is connected to
const int oneWireBus = 4;     

// WiFi credentials
const char* ssid = "Freebox-1AD904";
const char* password = "avocet#-ratam9%-devoraret#3-atriplex64";

// Server endpoint
const char* serverUrl = "http://192.168.1.35:8000/temperature";

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(oneWireBus);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

void setup() {
  // Start the Serial Monitor
  Serial.begin(9600);
  // Start the DS18B20 sensor
  sensors.begin();
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void loop() {
  sensors.requestTemperatures(); 
  float temperatureC = sensors.getTempCByIndex(0);
  Serial.print("Temperature: ");
  Serial.println(temperatureC);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    String payload = String("{\"temperature\":") + String(temperatureC, 2) + "}";
    int httpResponseCode = http.POST(payload);
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
  delay(5000); // Send every 5 seconds
}