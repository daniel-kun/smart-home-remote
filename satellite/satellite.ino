/*
This is the code of the Smart Home Remote satellite.

A satellite is a mobile (battery-powered) device that sends control signals to the "center" server.
The communication is via Bluetooth LE notifications.

This code runs on an ESP32 and sends out notifications when attached buttons are triggered.
*/
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
//#include <driver/gpio.h>

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;

#define SERVICE_UUID        "6f7f1a1c-d24d-40ff-83e1-552994ed1465"
#define CHARACTERISTIC_UUID "99ca7635-879d-4b08-bca1-0a8ba1ff0d47"

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      BLEDevice::startAdvertising();
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
    }
};

struct button_t {
  button_t(int buttonPin): pin(buttonPin), lastState(0)
  {
  };
  int pin;
  //gpio_num_t pin;     // the number of the pushbutton pin
  uint8_t lastState; // the last known button state
};

// Labels are when viewing from top, with the esp32 chip on top.
// numbers starting from bottom:
button_t buttons[10] = {
  button_t(32), // left, 1
  button_t(25), // left, 2
  button_t(33), // left, 3
  button_t(35), // left, 4
  button_t(34), // left, 5
  button_t(2), // right, 1
  button_t(4), // right, 2
  button_t(18), // right, 3
  button_t(22), // right, 4
  button_t(23)  // right, 5
};

void setup() {
  Serial.begin(115200);
  for (size_t i = 0; i < sizeof(buttons) / sizeof(buttons[0]); ++i) {
    const button_t & button = buttons[i];
    pinMode(button.pin, INPUT);
    //gpio_pad_select_gpio(button.pin);
    //gpio_set_direction(button.pin, GPIO_MODE_INPUT);
  }
  // Create the BLE Device
  BLEDevice::init("ESP32");

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_NOTIFY
                    );

  // https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.descriptor.gatt.client_characteristic_configuration.xml
  // Create a BLE Descriptor
  pCharacteristic->addDescriptor(new BLE2902());

  // Start the service
  pService->start();

  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);  // set value to 0x00 to not advertise this parameter
  BLEDevice::startAdvertising();
  Serial.println("Waiting for a client connection to notify...");
}

void loop() {
  for (size_t i = 0; i < sizeof(buttons) / sizeof(buttons[0]); ++i) {
    button_t & button = buttons[i];
    uint16_t newButtonState = static_cast<uint16_t>(digitalRead(button.pin));
    if (newButtonState != button.lastState) {
      button.lastState = newButtonState;
      Serial.print("Notifying about ");
      Serial.print(button.lastState);
      Serial.print(" on PIN ");
      Serial.println(button.pin);
      uint16_t value = button.lastState;
      value = value << 8;
      value |= button.pin;
      pCharacteristic->setValue(reinterpret_cast<uint8_t *>(&value), sizeof(uint16_t));
      pCharacteristic->notify();
      delay(6);
    }
  }
  // disconnecting
  if (!deviceConnected && oldDeviceConnected) {
      delay(500); // give the bluetooth stack the chance to get things ready
      pServer->startAdvertising(); // restart advertising
      Serial.println("Restarted advertising");
      oldDeviceConnected = deviceConnected;
  }
  // connecting
  if (deviceConnected && !oldDeviceConnected) {
      // do stuff here on connecting
      Serial.println("Welcome, a client connected");
      oldDeviceConnected = deviceConnected;
  }
//  delay(10); // sampling rate
}
