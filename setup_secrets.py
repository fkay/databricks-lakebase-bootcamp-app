"""One-time setup script for the support ticket Lakebase app."""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
import getpass

w = WorkspaceClient()

w.secrets.create_scope(scope="database")
w.secrets.put_secret(
    scope="database",
    key="lakebase-url",
    string_value=getpass.getpass("Paste your Lakebase URL: "),
)

# w.secrets.put_secret(
#     scope="database",
#     key="geocode-xyz-api-key",
#     string_value=getpass.getpass("Paste your geocode.xyz API key: "),
# )

w.secrets.put_secret(
    scope="database",
    key="geopy-app-name",
    string_value=getpass.getpass("Paste your geocode.xyz API key: "),
)

w.secrets.put_acl(
    scope="database",
    principal="users",
    permission=workspace.AclPermission.READ,
)
