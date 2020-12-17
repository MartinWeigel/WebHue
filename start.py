from waitress import serve
import webhue
serve(webhue.app, host='0.0.0.0', port=8080)
