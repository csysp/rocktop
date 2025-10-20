package k8s.policy

# Disallow cluster-scoped RBAC to encourage namespace-scoped permissions.

deny[msg] {
  input.kind == "ClusterRole"
  msg := "ClusterRole is disallowed; use Role in a namespace"
}

deny[msg] {
  input.kind == "ClusterRoleBinding"
  msg := "ClusterRoleBinding is disallowed; use RoleBinding in a namespace"
}

