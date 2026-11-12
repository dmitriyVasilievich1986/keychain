# Terraform — GCP infrastructure

Infrastructure for running Keychain on Google Cloud. For now it contains:

- **Artifact Registry** — a Docker repository that stores the `keychain-backend` image,
  with cleanup policies (keep the 10 most recent versions, delete untagged images after 7 days).
- **Firestore** — the project's `(default)` database (Native mode, delete protection and
  point-in-time recovery on), which is the one eligible for Firestore's free tier. For
  extra environments set `firestore_database_name` (e.g. `keychain`) and `env` (e.g. `-dev`)
  to get a named database such as `keychain-dev`. The `password` and `users` collections are created by
  the backend on its first write; Terraform cannot create empty collections.

## Layout

```
terraform/
├── main.tf, variables.tf, outputs.tf   # root config: wires the modules together
├── providers.tf, versions.tf
└── modules/
    ├── artifact_registry/              # Docker repository + cleanup policies
    └── firestore/                      # Firestore database (password + users collections)
```

Each piece of infrastructure lives in its own module under `modules/`; the root
config only passes variables in and exposes outputs.

## Prerequisites

- Terraform >= 1.6
- `gcloud` authenticated with an account that can manage the project:

  ```bash
  gcloud auth application-default login
  ```

## Usage

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # set project_id and region
terraform init
terraform plan
terraform apply
```

## Pushing the backend image

```bash
gcloud auth configure-docker <region>-docker.pkg.dev
IMAGE=$(terraform output -raw backend_image)
docker build -t "$IMAGE:latest" ..
docker push "$IMAGE:latest"
```

## State

State is stored locally (`terraform.tfstate`, git-ignored). Move it to a GCS
backend before sharing the setup or running it from CI.
