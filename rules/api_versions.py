"""Kubernetes API removals documented in the Deprecated API Migration Guide."""

from __future__ import annotations

import re

# https://kubernetes.io/docs/reference/using-api/deprecation-guide/#removed-apis-by-release
# Each entry is keyed by group/version and kind, with the first release
# that stopped serving it and a migration target.
REMOVED_APIS = {
    ("extensions/v1beta1", "NetworkPolicy"): (16, "Migrar para networking.k8s.io/v1"),
    ("extensions/v1beta1", "DaemonSet"): (16, "Migrar para apps/v1"),
    ("extensions/v1beta1", "Deployment"): (16, "Migrar para apps/v1"),
    ("extensions/v1beta1", "ReplicaSet"): (16, "Migrar para apps/v1"),
    ("apps/v1beta1", "Deployment"): (16, "Migrar para apps/v1"),
    ("apps/v1beta2", "Deployment"): (16, "Migrar para apps/v1"),
    ("apps/v1beta2", "DaemonSet"): (16, "Migrar para apps/v1"),
    ("apps/v1beta1", "StatefulSet"): (16, "Migrar para apps/v1"),
    ("apps/v1beta2", "StatefulSet"): (16, "Migrar para apps/v1"),
    ("apps/v1beta1", "ReplicaSet"): (16, "Migrar para apps/v1"),
    ("apps/v1beta2", "ReplicaSet"): (16, "Migrar para apps/v1"),
    ("extensions/v1beta1", "PodSecurityPolicy"): (16, "Migrar para Pod Security Admission"),
    ("extensions/v1beta1", "Ingress"): (22, "Migrar para networking.k8s.io/v1"),
    ("networking.k8s.io/v1beta1", "Ingress"): (22, "Migrar para networking.k8s.io/v1"),
    ("networking.k8s.io/v1beta1", "IngressClass"): (22, "Migrar para networking.k8s.io/v1"),
    ("apiextensions.k8s.io/v1beta1", "CustomResourceDefinition"): (22, "Migrar para apiextensions.k8s.io/v1"),
    ("admissionregistration.k8s.io/v1beta1", "MutatingWebhookConfiguration"): (22, "Migrar para admissionregistration.k8s.io/v1"),
    ("admissionregistration.k8s.io/v1beta1", "ValidatingWebhookConfiguration"): (22, "Migrar para admissionregistration.k8s.io/v1"),
    ("apiregistration.k8s.io/v1beta1", "APIService"): (22, "Migrar para apiregistration.k8s.io/v1"),
    ("authentication.k8s.io/v1beta1", "TokenReview"): (22, "Migrar para authentication.k8s.io/v1"),
    ("authorization.k8s.io/v1beta1", "LocalSubjectAccessReview"): (22, "Migrar para authorization.k8s.io/v1"),
    ("authorization.k8s.io/v1beta1", "SelfSubjectAccessReview"): (22, "Migrar para authorization.k8s.io/v1"),
    ("authorization.k8s.io/v1beta1", "SubjectAccessReview"): (22, "Migrar para authorization.k8s.io/v1"),
    ("certificates.k8s.io/v1beta1", "CertificateSigningRequest"): (22, "Migrar para certificates.k8s.io/v1"),
    ("coordination.k8s.io/v1beta1", "Lease"): (22, "Migrar para coordination.k8s.io/v1"),
    ("rbac.authorization.k8s.io/v1beta1", "ClusterRole"): (22, "Migrar para rbac.authorization.k8s.io/v1"),
    ("rbac.authorization.k8s.io/v1beta1", "ClusterRoleBinding"): (22, "Migrar para rbac.authorization.k8s.io/v1"),
    ("rbac.authorization.k8s.io/v1beta1", "Role"): (22, "Migrar para rbac.authorization.k8s.io/v1"),
    ("rbac.authorization.k8s.io/v1beta1", "RoleBinding"): (22, "Migrar para rbac.authorization.k8s.io/v1"),
    ("scheduling.k8s.io/v1beta1", "PriorityClass"): (22, "Migrar para scheduling.k8s.io/v1"),
    ("storage.k8s.io/v1beta1", "CSIDriver"): (22, "Migrar para storage.k8s.io/v1"),
    ("storage.k8s.io/v1beta1", "CSINode"): (22, "Migrar para storage.k8s.io/v1"),
    ("storage.k8s.io/v1beta1", "StorageClass"): (22, "Migrar para storage.k8s.io/v1"),
    ("storage.k8s.io/v1beta1", "VolumeAttachment"): (22, "Migrar para storage.k8s.io/v1"),
    ("autoscaling/v2beta1", "HorizontalPodAutoscaler"): (25, "Migrar para autoscaling/v2"),
    ("batch/v1beta1", "CronJob"): (25, "Migrar para batch/v1"),
    ("discovery.k8s.io/v1beta1", "EndpointSlice"): (25, "Migrar para discovery.k8s.io/v1"),
    ("events.k8s.io/v1beta1", "Event"): (25, "Migrar para events.k8s.io/v1"),
    ("node.k8s.io/v1beta1", "RuntimeClass"): (25, "Migrar para node.k8s.io/v1"),
    ("policy/v1beta1", "PodDisruptionBudget"): (25, "Migrar para policy/v1 e revisar o seletor"),
    ("policy/v1beta1", "PodSecurityPolicy"): (25, "Migrar para Pod Security Admission"),
    ("autoscaling/v2beta2", "HorizontalPodAutoscaler"): (26, "Migrar para autoscaling/v2"),
    ("storage.k8s.io/v1beta1", "CSIStorageCapacity"): (27, "Migrar para storage.k8s.io/v1"),
    ("flowcontrol.apiserver.k8s.io/v1beta1", "FlowSchema"): (26, "Migrar para uma versão servida de flowcontrol.apiserver.k8s.io"),
    ("flowcontrol.apiserver.k8s.io/v1beta1", "PriorityLevelConfiguration"): (26, "Migrar para uma versão servida de flowcontrol.apiserver.k8s.io"),
    ("flowcontrol.apiserver.k8s.io/v1beta2", "FlowSchema"): (29, "Migrar para flowcontrol.apiserver.k8s.io/v1"),
    ("flowcontrol.apiserver.k8s.io/v1beta2", "PriorityLevelConfiguration"): (29, "Migrar para flowcontrol.apiserver.k8s.io/v1"),
    ("flowcontrol.apiserver.k8s.io/v1beta3", "FlowSchema"): (32, "Migrar para flowcontrol.apiserver.k8s.io/v1"),
    ("flowcontrol.apiserver.k8s.io/v1beta3", "PriorityLevelConfiguration"): (32, "Migrar para flowcontrol.apiserver.k8s.io/v1"),
}


def version_minor(value: str) -> int:
    match = re.fullmatch(r"v?1\.(0|[1-9][0-9]*)(?:\.[0-9]+)?", value)
    if match is None:
        raise ValueError("Use uma versão Kubernetes 1.x, por exemplo 1.32 ou v1.32.1.")
    return int(match[1])
