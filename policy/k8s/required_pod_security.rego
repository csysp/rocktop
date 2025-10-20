package k8s.policy

# Enforce baseline pod/container security hardening.

default deny = []

pod_spec := input.spec.template.spec
pod_spec := input.spec { not input.spec.template }

# Require runAsNonRoot at pod or container level.
deny[msg] {
  not has_run_as_non_root(pod_spec)
  msg := "pod security: runAsNonRoot=true is required at pod or container level"
}

has_run_as_non_root(pod) {
  pod.securityContext.runAsNonRoot == true
}

has_run_as_non_root(pod) {
  some i
  pod.containers[i].securityContext.runAsNonRoot == true
}

# Forbid privileged containers.
deny[msg] {
  some i
  pod_spec.containers[i].securityContext.privileged == true
  msg := sprintf("container '%s' must not set privileged=true", [pod_spec.containers[i].name])
}

# Enforce runAsUser UID >= 1000 at pod or container level when specified.
deny[msg] {
  pod_spec.securityContext.runAsUser < 1000
  msg := "pod security: runAsUser must be >= 1000"
}

deny[msg] {
  some i
  u := pod_spec.containers[i].securityContext.runAsUser
  u < 1000
  msg := sprintf("container '%s' runAsUser must be >= 1000", [pod_spec.containers[i].name])
}

# Apply the same container-level checks to initContainers if present.
deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  not c.securityContext
  msg := sprintf("initContainer '%s' missing securityContext", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  c.securityContext.privileged == true
  msg := sprintf("initContainer '%s' must not set privileged=true", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  c.securityContext.allowPrivilegeEscalation != false
  msg := sprintf("initContainer '%s' must set allowPrivilegeEscalation=false", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  c.securityContext.readOnlyRootFilesystem != true
  msg := sprintf("initContainer '%s' must set readOnlyRootFilesystem=true", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  not c.securityContext.capabilities
  msg := sprintf("initContainer '%s' missing capabilities drop", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  not capabilities_drop_all(c)
  msg := sprintf("initContainer '%s' must drop ALL capabilities", [c.name])
}

# Require seccompProfile RuntimeDefault at pod or container level.
deny[msg] {
  not has_seccomp_runtime_default(pod_spec)
  msg := "pod security: seccompProfile.type=RuntimeDefault is required"
}

has_seccomp_runtime_default(pod) {
  pod.securityContext.seccompProfile.type == "RuntimeDefault"
}

has_seccomp_runtime_default(pod) {
  some i
  pod.containers[i].securityContext.seccompProfile.type == "RuntimeDefault"
}

# For each container, enforce hardened settings.
deny[msg] {
  some i
  c := pod_spec.containers[i]
  not c.securityContext
  msg := sprintf("container '%s' missing securityContext", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.containers[i]
  not c.securityContext.allowPrivilegeEscalation
  c.name == c.name
  msg := sprintf("container '%s' missing allowPrivilegeEscalation=false", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.containers[i]
  c.securityContext.allowPrivilegeEscalation != false
  msg := sprintf("container '%s' must set allowPrivilegeEscalation=false", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.containers[i]
  c.securityContext.readOnlyRootFilesystem != true
  msg := sprintf("container '%s' must set readOnlyRootFilesystem=true", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.containers[i]
  not c.securityContext.capabilities
  msg := sprintf("container '%s' missing capabilities drop", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.containers[i]
  not capabilities_drop_all(c)
  msg := sprintf("container '%s' must drop ALL capabilities", [c.name])
}

capabilities_drop_all(c) {
  some j
  c.securityContext.capabilities.drop[j] == "ALL"
}
