{{- define "nufi.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "nufi.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "nufi.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | quote }}
app.kubernetes.io/name: {{ include "nufi.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: nufi
{{- end -}}

{{- define "nufi.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nufi.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "nufi.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "nufi.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{- define "nufi.configMapName" -}}
{{ include "nufi.fullname" . }}-config
{{- end -}}

{{- define "nufi.secretName" -}}
{{- if .Values.secret.create -}}
{{- default (printf "%s-secret" (include "nufi.fullname" .)) .Values.secret.name -}}
{{- else -}}
{{- required "secret.name is required when secret.create=false" .Values.secret.name -}}
{{- end -}}
{{- end -}}

{{- define "nufi.mediaPvcName" -}}
{{ include "nufi.fullname" . }}-media
{{- end -}}

{{- define "nufi.reportsPvcName" -}}
{{ include "nufi.fullname" . }}-reports
{{- end -}}

{{- define "nufi.allowedHosts" -}}
{{- $fullname := include "nufi.fullname" . -}}
{{- $namespace := .Release.Namespace -}}
{{- $internalHosts := printf "%s,%s.%s,%s.%s.svc,%s.%s.svc.cluster.local" $fullname $fullname $namespace $fullname $namespace $fullname $namespace -}}
{{- if .Values.env.allowedHosts -}}
{{- printf "%s,%s" .Values.env.allowedHosts $internalHosts -}}
{{- else -}}
{{- $internalHosts -}}
{{- end -}}
{{- end -}}
