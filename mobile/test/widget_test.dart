import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/main.dart';

void main() {
  testWidgets('Verificar carga de SMATApp sin fallas', (WidgetTester tester) async {
    // Construimos nuestra aplicación real (SMATApp)
    await tester.pumpWidget(const SMATApp());

    // Verificamos que la barra superior se cargue con el título correcto
    expect(find.text('Estaciones SMAT'), findsOneWidget);
  });
}
