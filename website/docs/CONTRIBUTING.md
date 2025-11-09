# 贡献指南

感谢你考虑为这个项目做贡献！

### 我应该如何贡献？

首先，访问我们的[植物大战僵尸Python版官方仓库](https://github.com/Find1134/plants-vs-zombies-source)，点击右上角的`Fork`，这样，你就克隆了一个植物大战僵尸Python版仓库，你就可以在这个仓库中进行直接修改了。

然后打开你的Windows终端，命令提示符也不错。依次输入以下命令：

```bash
git clone https://github.com/【你的用户名】/plants-vs-zombies-source.git
cd plants-vs-zombies-source
git init
git remote add origin https://github.com/【你的用户名】/plants-vs-zombies-source.git
git branch -m main
```

输入以上命令后打开你的本地克隆仓库，你就可以在里面进行修改了。

### 如何上交更改？

很简单，还是打开Windows终端，确保Windows终端位于你的Fork仓库的**根目录**，然后依次输入以下命令：

```bash
git add .
git commit -m "你的提交理由"
git pull
git push -u origin main		# 之后更改Fork仓库的话仅需输入git push即可
```

依次输入好以上命令后，访问你的Fork仓库，点击`Pull Request`按钮，这会像我们发起拉取请求，我们会检查你的拉取请求请求中的代码，确保没有恶意代码等东西后就会合并你的Fork。

---

到这里，就算这贡献完毕啦！