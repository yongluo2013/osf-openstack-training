[root@devstack python-novaclient]# git status
# On branch master
# Changed but not updated:
#   (use "git add <file>..." to update what will be committed)
#   (use "git checkout -- <file>..." to discard changes in working directory)
#
#	modified:   novaclient/v1_1/shell.py
#
# Untracked files:
#   (use "git add <file>..." to include in what will be committed)
#
#	novaclient/tests/v1_1/contrib/test_documents.py
#	novaclient/v1_1/contrib/documents.py
no changes added to commit (use "git add" and/or "git commit -a")

[root@devstack python-novaclient]# git diff
diff --git a/novaclient/v1_1/shell.py b/novaclient/v1_1/shell.py
index eb5b39a..862f578 100644
--- a/novaclient/v1_1/shell.py
+++ b/novaclient/v1_1/shell.py
@@ -3936,3 +3936,7 @@ def do_version_list(cs, args):
     result = cs.versions.list()
     columns = ["Id", "Status", "Updated"]
     utils.print_list(result, columns)
+def do_document_list(cs, args):
+    result = cs.documents.list()
+    columns = ["Id", "Name"]
+    utils.print_list(result, columns)