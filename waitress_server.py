from waitress import serve
import myApp
serve(myApp.app.server, host='0.0.0.0', port=8091)