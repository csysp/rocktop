package k8s.policy

# Require cpu/memory requests and limits for all containers.

default deny = []

pod_spec := input.spec.template.spec
pod_spec := input.spec { not input.spec.template }

deny[msg] {
  some i
  c := pod_spec.containers[i]
  not c.resources
  msg := sprintf("container '%s' missing resources", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.containers[i]
  not c.resources.requests
  msg := sprintf("container '%s' missing resources.requests", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.containers[i]
  not c.resources.limits
  msg := sprintf("container '%s' missing resources.limits", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.containers[i]
  not c.resources.requests.cpu
  msg := sprintf("container '%s' missing requests.cpu", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.containers[i]
  not c.resources.requests.memory
  msg := sprintf("container '%s' missing requests.memory", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.containers[i]
  not c.resources.limits.cpu
  msg := sprintf("container '%s' missing limits.cpu", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.containers[i]
  not c.resources.limits.memory
  msg := sprintf("container '%s' missing limits.memory", [c.name])
}

# Apply the same requirements to initContainers if present.
deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  not c.resources
  msg := sprintf("initContainer '%s' missing resources", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  not c.resources.requests
  msg := sprintf("initContainer '%s' missing resources.requests", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  not c.resources.limits
  msg := sprintf("initContainer '%s' missing resources.limits", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  not c.resources.requests.cpu
  msg := sprintf("initContainer '%s' missing requests.cpu", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  not c.resources.requests.memory
  msg := sprintf("initContainer '%s' missing requests.memory", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  not c.resources.limits.cpu
  msg := sprintf("initContainer '%s' missing limits.cpu", [c.name])
}

deny[msg] {
  some i
  c := pod_spec.initContainers[i]
  not c.resources.limits.memory
  msg := sprintf("initContainer '%s' missing limits.memory", [c.name])
}
