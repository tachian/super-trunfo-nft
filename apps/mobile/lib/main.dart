import 'package:flutter/material.dart';

import 'src/app.dart';
import 'src/config/app_environment.dart';

void main() {
  runApp(
    SuperTrunfoApp(environment: AppEnvironment.fromDartDefines()),
  );
}
