terraform {
    cloud {
        organization = "Macksbusiness"

        workspaces {
            name = "privatework"
            project = "Default Project"
        }
    }
}
