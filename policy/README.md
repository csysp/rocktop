Kubernetes OPA Policies (Conftest)

Policies applied in CI to guard common pitfalls:

- deny_latest_tag.rego: Forbid images using `:latest` or missing tags.
- required_labels.rego: Require `app` and `owner` labels on resources and pod templates.
- disallow_cluster_scoped_rbac.rego: Disallow ClusterRole/ClusterRoleBinding.

Run locally:

  conftest test -p policy/k8s k8s

