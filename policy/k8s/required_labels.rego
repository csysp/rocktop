package k8s.policy

# Require minimal labels at both resource and pod template level.

required := {"app", "owner"}

deny[msg] {
  some k
  k := required[_]
  not has_label(input.metadata.labels, k)
  msg := sprintf("missing required label '%s' on resource metadata", [k])
}

deny[msg] {
  input.spec.template
  some k
  k := required[_]
  not has_label(input.spec.template.metadata.labels, k)
  msg := sprintf("missing required label '%s' on pod template", [k])
}

has_label(labels, key) {
  labels[key]
}

