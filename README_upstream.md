在 Git 中，fork 一个仓库意味着创建一个原仓库的副本。当原仓库有更新时，你可能希望将这些更新合并到你的 fork 仓库。以下是更新 fork 仓库的步骤：

1. 首先，确保你已经安装了 Git 并在本地配置好了你的 fork 仓库。如果还没有，请参考 [GitHub 文档](https://docs.github.com/en/get-started/quickstart/fork-a-repo)。

2. 打开命令行或终端，切换到你的本地仓库目录。例如：

   ```
   cd /path/to/your/forked/repo
   ```

3. 添加原仓库作为一个新的远程仓库，通常命名为 "upstream"。将 `https://github.com/ORIGINAL_OWNER/ORIGINAL_REPOSITORY.git` 替换为原仓库的 URL：

   ```
   git remote add upstream https://github.com/ORIGINAL_OWNER/ORIGINAL_REPOSITORY.git
   ```

   你可以使用 `git remote -v` 命令查看已添加的远程仓库。

4. 获取原仓库的更新：

   ```
   git fetch upstream
   ```

   这将会下载原仓库的所有更新，但不会自动合并到你的本地分支。


