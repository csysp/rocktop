package k8s.policy

# Deny images using the ':latest' tag or missing a tag.

default deny = []

deny[msg] {
  some c
  image := container_images[c]
  endswith(image, ":latest")
  msg := sprintf("container uses forbidden tag ':latest': %s", [image])
}

deny[msg] {
  some c
  image := container_images[c]
  not contains(image, ":")
  msg := sprintf("container image missing explicit tag: %s", [image])
}

# Collect container image strings across common K8s objects.
container_images[i] := img {
  some i
  img := input.spec.template.spec.containers[i].image
}

container_images[i] := img {
  some i
  img := input.spec.template.spec.initContainers[i].image
}

container_images[i] := img {
  some i
  img := input.spec.containers[i].image
}

container_images[i] := img {
  some i
  img := input.spec.initContainers[i].image
}

