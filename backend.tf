terraform {
    cloud {
        organization = "REPLACE_WITH_YOUR_ORGANIZATION_NAME"

        workspaces {
            name = "REPLACE_WITH_YOUR_WORKSPACE_NAME"
            project = "REPLACE_WITH_YOUR_PROJECT_NAME"
        }
    }
}
