{{- define "platform-api.name" -}}{{ .Chart.Name }}{{- end }}
{{- define "platform-api.labels" -}}
app.kubernetes.io/name: {{ include "platform-api.name" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
