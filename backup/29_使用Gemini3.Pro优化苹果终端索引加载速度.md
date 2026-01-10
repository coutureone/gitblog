# [使用Gemini3 Pro优化苹果终端索引加载速度](https://github.com/coutureone/gitblog/issues/29)


&ensp;自己一开始对苹果终端索引加载速度并不是很在意，毕竟随着自己用到的环境变量越来越多，终端加载速度越来越慢，慢到了超出了我难以接受的范围，加载索引都要5秒左右，测试一个`ping`都要等索引加载一段时间才可以，于是自己想到了用AI去优化这个索引加载。

&ensp;提出需求：

![](https://cdn.jsdelivr.net/gh/coutureone/gitblog@main/img/image-20260110142458293.png)

&ensp;我的三个配置文件分别如下：

`.zshrc`:

```bash
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="powerlevel10k/powerlevel10k"


plugins=(git autojump zsh-autosuggestions zsh-syntax-highlighting)

source $ZSH/oh-my-zsh.sh

eval "$(/opt/homebrew/bin/brew shellenv)"
DISABLE_MAGIC_FUNCTIONS=true
 zstyle ':omz:update' mode disabled
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
export PATH="$HOME/.jenv/bin:$PATH"
eval "$(jenv init -)"

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
export PATH="/opt/homebrew/opt/node@20/bin:$PATH"


# maven
export MAVEN_HOME="$HOME/Java Development/apache-maven-3.8.8"
export PATH="$MAVEN_HOME/bin:$PATH"

export PATH="/opt/homebrew/opt/openssl@3/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig"


export PATH="$HOME/bin:$PATH"

export PATH="/opt/homebrew/bin:$PATH"


# Created by `pipx` on 2024-11-09 06:23:41
export PATH="$PATH:/Users/couture/.local/bin"

# Python
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# rust
source $HOME/.cargo/env

# MySQL 
export PATH=$PATH:/usr/local/mysql/bin

# Go
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

# Added by LM Studio CLI (lms)
export PATH="$PATH:/Users/couture/.lmstudio/bin"

# Added by Antigravity
export PATH="/Users/couture/.antigravity/antigravity/bin:$PATH"

```

`.zprofile`:

```bash
eval "$(/opt/homebrew/bin/brew shellenv)"

# Created by `pipx` on 2024-11-09 06:23:41
export PATH="$PATH:/Users/couture/.local/bin"

# Setting PATH for Python 3.11
# The original version is saved in .zprofile.pysave
PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin:${PATH}"
export PATH

# Added by OrbStack: command-line tools and integration
# This won't be added again if you remove it.
source ~/.orbstack/shell/init.zsh 2>/dev/null || :

```

`.zshenv`:

```bash
. "$HOME/.cargo/env"
```

&ensp;优化以后的输出结果

```bash
# [1] Powerlevel10k Instant Prompt (必须放在文件最开头)
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# [2] 基础环境变量与 PATH 优化 (合并所有 PATH 设置)
# Homebrew (首先加载，确保基础命令可用)
eval "$(/opt/homebrew/bin/brew shellenv)"

# 定义路径变量
export GOPATH="$HOME/go"
export MAVEN_HOME="$HOME/Java Development/apache-maven-3.8.8"

# 编译器标志 (OpenSSL)
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig"

# 批量构建 PATH (注意顺序：自定义 > Homebrew > 系统)
# 包含: Node@20, OpenJDK@17, Maven, MySQL, Go, LM Studio, Antigravity, User Bins
path=(
  "$HOME/bin"
  "$HOME/.local/bin"
  "/opt/homebrew/opt/node@20/bin"
  "/opt/homebrew/opt/openjdk@17/bin"
  "$MAVEN_HOME/bin"
  "/usr/local/mysql/bin"
  "$GOPATH/bin"
  "$HOME/.pyenv/bin"
  "$HOME/.lmstudio/bin"
  "/Users/couture/.antigravity/antigravity/bin"
  "/Library/Frameworks/Python.framework/Versions/3.11/bin"
  $path
)
export PATH

# [3] Oh My Zsh 配置
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"
# 禁用自动更新检查 (提升启动速度)
zstyle ':omz:update' mode disabled 
# 禁用魔法函数 (解决粘贴 URL 问题)
DISABLE_MAGIC_FUNCTIONS="true"

# 插件加载 (注意：过多插件会拖慢速度，当前保留了你原本的)
plugins=(git autojump zsh-autosuggestions zsh-syntax-highlighting)

source $ZSH/oh-my-zsh.sh

# [4] 懒加载优化 (Lazy Loading) - 极大提升速度的关键
# 只有当你输入 jenv 或 java 相关命令时，才会初始化 jenv
if [ -d "$HOME/.jenv" ]; then
  export PATH="$HOME/.jenv/bin:$PATH"
  function jenv() {
    unset -f jenv
    eval "$(jenv init -)"
    jenv "$@"
  }
fi

# 只有当你输入 pyenv 时才初始化 (常规 python 命令走 PATH 即可)
if command -v pyenv 1>/dev/null 2>&1; then
  function pyenv() {
    unset -f pyenv
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    pyenv "$@"
  }
fi

# Rust (Cargo) 保持标准加载，速度通常很快
[[ -f "$HOME/.cargo/env" ]] && . "$HOME/.cargo/env"

# OrbStack
[[ -f ~/.orbstack/shell/init.zsh ]] && source ~/.orbstack/shell/init.zsh 2>/dev/null || :

# [5] P10k 配置文件
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
```

&ensp;现在打开终端以后打开的速度瞬间打开，启用优化后的环境变量以后，用`source`命令进行刷新，如果对AI不放心我采取的是给自己原来配置的环境变量进行备份。