/*
 * Proyecto: Monitoreo de EPP en Área de Torno
 * Dispositivo: Arduino Mega 2560
 * Descripción: Control de alertas locales mediante comandos Serial.
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Configuración de la pantalla LCD I2C (Dirección 0x27 y tamaño 16x2)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Definición de pines
const int LED_VERDE = 2;
const int LED_ROJO = 3;
const int BUZZER = 4;

void setup() {
  // Inicialización de Serial a 9600 baudios
  Serial.begin(9600);
  
  // Configuración de pines de salida
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  
  // Inicialización de LCD
  lcd.init();
  lcd.backlight();
  mostrarEstadoReposo();
}

void loop() {
  // Verificar si hay datos disponibles en el puerto serie
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim(); // Eliminar espacios o saltos de línea

    if (comando == "OK") {
      ejecutarAccesoConcedido();
    } 
    else if (comando.startsWith("FALTA:")) {
      // El comando esperado es algo como "FALTA: Casco, Guantes"
      ejecutarAlarma(comando.substring(6)); 
    }
  }
}

void mostrarEstadoReposo() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("SISTEMA EPP");
  lcd.setCursor(0, 1);
  lcd.print("ESPERANDO...");
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_ROJO, LOW);
}

void ejecutarAccesoConcedido() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("EQUIPO COMPLETO");
  lcd.setCursor(0, 1);
  lcd.print("ACCESO OK");
  
  digitalWrite(LED_VERDE, HIGH);
  delay(2000); // Luz verde por 2 segundos según requerimiento
  digitalWrite(LED_VERDE, LOW);
  
  mostrarEstadoReposo();
}

void ejecutarAlarma(String faltantes) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("ALERTA: FALTANTE");
  lcd.setCursor(0, 1);
  lcd.print(faltantes.substring(0, 16)); // Mostrar lo que quepa en la pantalla

  // Simulación de alarma (LED Rojo parpadeando y sonido)
  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_ROJO, HIGH);
    tone(BUZZER, 1000); // Frecuencia de 1000Hz
    delay(300);
    digitalWrite(LED_ROJO, LOW);
    noTone(BUZZER);
    delay(300);
  }
  
  mostrarEstadoReposo();
}
