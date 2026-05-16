import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/estacion.dart';

class ApiService {
  // Usamos 127.0.0.1 para Google Chrome (Web)
  final String baseUrl = "http://127.0.0.1:8000"; 

  // --- AYUDANTE PRIVADO PARA OBTENER EL TOKEN ---
  Future<String?> _obtenerToken() async {
    try {
      final tokenResponse = await http.post(
        Uri.parse('$baseUrl/token'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'username': 'admin', 'password': 'admin'}),
      ).timeout(const Duration(seconds: 5)); // Lab 7.1: Timeout
      
      if (tokenResponse.statusCode == 200) {
        return json.decode(tokenResponse.body)['access_token'];
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  // 1. LEER (GET Público) - Lab 7.1: Manejo de Errores Robustos
  Future<List<Estacion>> fetchEstaciones() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/estaciones/'))
          .timeout(const Duration(seconds: 5)); // Lab 7.1: Evita esperas infinitas

      if (response.statusCode == 200) {
        List jsonResponse = json.decode(response.body);
        return jsonResponse.map((data) => Estacion.fromJson(data)).toList();
      } else {
        throw Exception('Error del servidor: ${response.statusCode}');
      }
    } catch (e) {
      // Lab 7.1: Evita que la app se cierre inesperadamente
      throw Exception('No se pudo conectar con SMAT. ¿Está el servidor activo?');
    }
  }

  // 2. CREAR (POST Protegido)
  Future<bool> crearEstacion(int id, String nombre, String ubicacion) async {
    final token = await _obtenerToken();
    if (token == null) return false;

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/estaciones/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({'id': id, 'nombre': nombre, 'ubicacion': ubicacion}),
      ).timeout(const Duration(seconds: 5));
      
      return response.statusCode == 201 || response.statusCode == 200; 
    } catch (e) {
      return false;
    }
  }

  // 3. EDITAR (PUT Protegido) - Lab 6.2
  Future<bool> editarEstacion(int id, String nuevoNombre, String nuevaUbicacion) async {
    final token = await _obtenerToken();
    if (token == null) return false;

    try {
      final uri = Uri.parse('$baseUrl/estaciones/$id?nombre=$nuevoNombre&ubicacion=$nuevaUbicacion');
      final response = await http.put(
        uri,
        headers: {'Authorization': 'Bearer $token'},
      ).timeout(const Duration(seconds: 5));
      
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // 4. ELIMINAR (DELETE Protegido) - Lab 6.2
  Future<bool> eliminarEstacion(int id) async {
    final token = await _obtenerToken();
    if (token == null) return false;

    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/estaciones/$id'),
        headers: {'Authorization': 'Bearer $token'},
      ).timeout(const Duration(seconds: 5));
      
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // 5. OBTENER RIESGO PARA EL RETO (GET Público)
  Future<String> obtenerNivelRiesgo(int id) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/estaciones/$id/riesgo'))
          .timeout(const Duration(seconds: 3));
      if (response.statusCode == 200) {
        return json.decode(response.body)['nivel']; // Retorna "NORMAL", "ALERTA" o "PELIGRO"
      }
      return "DESCONOCIDO";
    } catch (e) {
      return "DESCONOCIDO";
    }
  }
}