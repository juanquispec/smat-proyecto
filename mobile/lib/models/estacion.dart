class Estacion {
  final int id;
  final String nombre;
  final String ubicacion;

  Estacion({
    required this.id,
    required this.nombre,
    required this.ubicacion,
  });

  // Este método convierte el JSON que envía FastAPI a un Objeto de Dart
  factory Estacion.fromJson(Map<String, dynamic> json) {
    return Estacion(
      id: json['id'],
      nombre: json['nombre'],
      ubicacion: json['ubicacion'],
    );
  }
}