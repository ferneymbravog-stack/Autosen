INSERT INTO `usuario` (`Id_usuario`, `Nombre`, `Correo`, `Contrasena`, `Rol`) VALUES
(1, 'Admin', 'admin@autosen.com', '$2y$12$hashDePruebaNoReal', 'ADMIN');

INSERT INTO `cliente` (`Id_cliente`, `Nombre_cliente`, `Apellido_cliente`, `Contrasena`, `Correo`, `Id_usuario`, `Estado`, `Telefono`) VALUES
(1, 'John', 'O\'Neil', '$2y$12$hash1', 'john@test.com', 1, 'activo', '3001234567'),
(2, 'Juan', 'Ro\'cio', '$2y$12$hash2', 'juan@test.com', NULL, 'bloqueado', '3007654321');

INSERT INTO `vehiculo` (`Id_vehiculo`, `Id_cliente`, `Nombre_vehiculo`, `Color`, `Marca`, `Modelo`, `Placa`, `Tipo_placa`, `elm_mac`) VALUES
(4, 1, 'Onix, el rojo', 'Rojo', 'Chevrolet', '2020-01-01', 'EMT262', 'publico', NULL);

INSERT INTO `sensores` (`Id_sensor`, `Nombre_sensor`, `Tipo_sensor`, `Tipo_daño`, `Nivel`, `Estado`, `Id_vehiculo`) VALUES
(21, 'Sensor Oxigeno', 'Oxigeno', 'Falla en mezcla\ncombustible', 50, NULL, 4),
(22, 'Sensor Temperatura', 'Temperatura', NULL, NULL, 'OK', 4);

INSERT INTO `lecturas` (`Id_lectura`, `Id_vehiculo`, `Nombre_sensor`, `Tipo_sensor`, `Valor`, `Unidad`, `Nivel`, `Estado`, `Fecha_lectura`) VALUES
(7, 4, 'Sensor Temperatura', 'Temperatura', 2345.5, 'C', 30, 'OK', '2026-09-14 20:04:25');

INSERT INTO `alertas` (`Id_alerta`, `Id_vehiculo`, `Nombre_sensor`, `Tipo_sensor`, `Valor`, `Nivel`, `Tipo`, `Mensaje`, `Leida`, `Fecha_alerta`) VALUES
(3, 4, 'Sensor Oxigeno', 'Oxigeno', 100.0, 80, 'falla', 'Falla crítica; revisar (motor)', 0, '2026-09-14 20:05:00');
