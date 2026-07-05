# -*- coding: utf-8 -*-
import argparse
import os
import re

import markdown
from feedgen.feed import FeedGenerator
from github import Github
from lxml.etree import CDATA
from marko.ext.gfm import gfm as marko

BLOG_URL = os.getenv("BLOG_URL", "https://blog.xcouture.cc").rstrip("/")
DEFAULT_BRANCH = os.getenv("DEFAULT_BRANCH", "master")

MD_HEAD = """**<p align="center">[Couture's Blog]({blog_url})</p>**
====

**<p align="center">用于记录一些琐碎</p>**


## 联系方式
- X：[@xcouturec](https://x.com/xcouturec)
- Telegram：[@couturecc](https://t.me/couturecc)
- Email：[couturecome@gmail.com](mailto:couturecome@gmail.@163.com)
- Blog：[{blog_url}]({blog_url})
- RSS：[RSS Feed](https://raw.githubusercontent.com/{repo_name}/{branch}/feed.xml)
"""

BACKUP_DIR = "backup"
ANCHOR_NUMBER = 5
TOP_ISSUES_LABELS = ["Top"]
TODO_ISSUES_LABELS = ["TODO"]
FRIENDS_LABELS = ["友链", "Friends"]
FRIENDS_ISSUE_NUMBER = os.getenv("FRIENDS_ISSUE_NUMBER", "44")
IGNORE_LABELS = TOP_ISSUES_LABELS + TODO_ISSUES_LABELS + FRIENDS_LABELS

FRIENDS_TABLE_HEAD = "| 名字 | 链接 | 描述 |\n| --- | --- | --- |\n"
FRIENDS_TABLE_TEMPLATE = "| {name} | {link} | {desc} |\n"
FRIENDS_INFO_KEYS = {
    "名字": "name",
    "链接": "link",
    "描述": "desc",
}
FRIENDS_SECTION_START = "<!-- friends:start -->"
FRIENDS_SECTION_END = "<!-- friends:end -->"
FRIENDS_COMMENT_FORMAT = """如果你想交换友链，请按下面格式评论；我点 ❤️ 后会自动收录。

名字：你的博客名
链接：https://example.com
描述：一句话介绍你的博客
"""


def get_me(user):
    return user.get_user().login


def is_me(issue, me):
    return issue.user.login == me


def is_hearted_by_me(comment, me):
    for reaction in comment.get_reactions():
        if reaction.content == "heart" and reaction.user.login == me:
            return True
    return False


def is_friend_comment_approved(comment, me):
    return comment.user.login == me or is_hearted_by_me(comment, me)


def escape_table_cell(value):
    return str(value or "").replace("\n", " ").replace("|", "\\|").strip()


def parse_friend_comment(body):
    info = {"name": "", "link": "", "desc": ""}
    for line in (body or "").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = re.split(r"[:：]", line, maxsplit=1)
        if len(parts) != 2:
            continue
        key = parts[0].strip()
        value = parts[1].strip()
        if key in FRIENDS_INFO_KEYS:
            info[FRIENDS_INFO_KEYS[key]] = value

    if not info["name"] or not info["link"]:
        return None
    if not re.match(r"^https?://", info["link"]):
        return None
    return info


def make_friend_table_row(friend):
    return FRIENDS_TABLE_TEMPLATE.format(
        name=escape_table_cell(friend["name"]),
        link=escape_table_cell(friend["link"]),
        desc=escape_table_cell(friend["desc"]),
    )


def get_friends_issues(repo):
    issues = []
    seen = set()

    if FRIENDS_ISSUE_NUMBER:
        try:
            issue = repo.get_issue(int(FRIENDS_ISSUE_NUMBER))
            issues.append(issue)
            seen.add(issue.number)
        except Exception as e:
            print(f"Cannot load friends issue #{FRIENDS_ISSUE_NUMBER}: {e}")

    for label in FRIENDS_LABELS:
        try:
            for issue in repo.get_issues(labels=(label,)):
                if issue.number not in seen:
                    issues.append(issue)
                    seen.add(issue.number)
        except Exception as e:
            print(f"Cannot load friends issues by label {label}: {e}")
    return issues


def collect_friend_links(repo, me):
    friend_rows = []
    friend_issues = get_friends_issues(repo)
    for issue in friend_issues:
        for comment in issue.get_comments():
            if not is_friend_comment_approved(comment, me):
                continue
            friend = parse_friend_comment(comment.body or "")
            if not friend:
                continue
            friend_rows.append(make_friend_table_row(friend))
    return friend_issues, friend_rows


def render_friends_table(friend_rows):
    if not friend_rows:
        return "<p>暂无已审核友链。</p>"
    table_md = FRIENDS_TABLE_HEAD + "".join(friend_rows)
    return markdown.markdown(table_md, output_format="html", extensions=["extra"])


def is_legacy_friend_format(body):
    return all(key in body for key in ("name:", "url:", "desc:"))


def build_friends_issue_body(issue, friends_html):
    body = (issue.body or "").strip()
    if FRIENDS_SECTION_START in body and FRIENDS_SECTION_END in body:
        before, rest = body.split(FRIENDS_SECTION_START, 1)
        _, after = rest.split(FRIENDS_SECTION_END, 1)
        return (
            before.rstrip()
            + "\n\n"
            + FRIENDS_SECTION_START
            + "\n"
            + friends_html
            + "\n"
            + FRIENDS_SECTION_END
            + after
        )

    intro = (
        FRIENDS_COMMENT_FORMAT
        if not body or is_legacy_friend_format(body)
        else body
    )
    return (
        intro.rstrip()
        + "\n\n---\n\n## 已收录\n\n"
        + FRIENDS_SECTION_START
        + "\n"
        + friends_html
        + "\n"
        + FRIENDS_SECTION_END
        + "\n"
    )


def sync_friends_issue(friend_issues, friends_html):
    if not friend_issues:
        return
    issue = friend_issues[0]
    next_body = build_friends_issue_body(issue, friends_html)
    if (issue.body or "").strip() == next_body.strip():
        return
    issue.edit(body=next_body)


# help to covert xml vaild string
def _valid_xml_char_ordinal(c):
    codepoint = ord(c)
    # conditions ordered by presumed frequency
    return (
        0x20 <= codepoint <= 0xD7FF
        or codepoint in (0x9, 0xA, 0xD)
        or 0xE000 <= codepoint <= 0xFFFD
        or 0x10000 <= codepoint <= 0x10FFFF
    )


def format_time(time):
    return str(time)[:10]


def login(token):
    return Github(token)


def get_repo(user: Github, repo: str):
    return user.get_repo(repo)


def parse_TODO(issue):
    body = issue.body.splitlines()
    todo_undone = [l for l in body if l.startswith("- [ ] ")]
    todo_done = [l for l in body if l.startswith("- [x] ")]
    # just add info all done
    if not todo_undone:
        return f"[{issue.title}]({issue.html_url}) all done", []
    return (
        f"[{issue.title}]({issue.html_url})--{len(todo_undone)} jobs to do--{len(todo_done)} jobs done",
        todo_done + todo_undone,
    )


def get_top_issues(repo):
    return repo.get_issues(labels=TOP_ISSUES_LABELS)


def get_todo_issues(repo):
    return repo.get_issues(labels=TODO_ISSUES_LABELS)


def get_repo_labels(repo):
    return [l for l in repo.get_labels()]


def get_issues_from_label(repo, label):
    return repo.get_issues(labels=(label,))


def add_issue_info(issue, md):
    time = format_time(issue.created_at)
    md.write(f"- [{issue.title}]({issue.html_url})--{time}\n")


def add_md_todo(repo, md, me):
    todo_issues = list(get_todo_issues(repo))
    if not TODO_ISSUES_LABELS or not todo_issues:
        return
    with open(md, "a+", encoding="utf-8") as md:
        md.write("## TODO\n")
        for issue in todo_issues:
            if is_me(issue, me):
                todo_title, todo_list = parse_TODO(issue)
                md.write("TODO list from " + todo_title + "\n")
                for t in todo_list:
                    md.write(t + "\n")
                # new line
                md.write("\n")


def add_md_top(repo, md, me):
    top_issues = list(get_top_issues(repo))
    if not TOP_ISSUES_LABELS or not top_issues:
        return
    with open(md, "a+", encoding="utf-8") as md:
        md.write("## 置顶文章\n")
        for issue in top_issues:
            if is_me(issue, me):
                add_issue_info(issue, md)


def add_md_friends(md, me, friend_issues, friend_rows):
    if not friend_issues:
        return
    friends_issue_number = friend_issues[0].number
    friends_html = render_friends_table(friend_rows)
    with open(md, "a+", encoding="utf-8") as md:
        md.write(
            f"## [友情链接](https://github.com/{me}/gitblog/issues/{friends_issue_number})\n"
        )
        md.write("<details><summary>显示</summary>\n")
        md.write(friends_html)
        md.write("\n</details>\n\n")


def add_md_recent(repo, md, me, limit=5):
    count = 0
    with open(md, "a+", encoding="utf-8") as md:
        # one the issue that only one issue and delete (pyGitHub raise an exception)
        try:
            md.write("## 最近更新\n")
            for issue in repo.get_issues():
                if is_me(issue, me):
                    add_issue_info(issue, md)
                    count += 1
                    if count >= limit:
                        break
        except Exception as e:
            print(str(e))


def add_md_header(md, repo_name):
    with open(md, "w", encoding="utf-8") as md:
        md.write(MD_HEAD.format(
            blog_url=BLOG_URL,
            branch=DEFAULT_BRANCH,
            repo_name=repo_name,
        ))
        md.write("\n")


def add_md_label(repo, md, me):
    labels = get_repo_labels(repo)

    # sort lables by description info if it exists, otherwise sort by name,
    # for example, we can let the description start with a number (1#Java, 2#Docker, 3#K8s, etc.)
    labels = sorted(
        labels,
        key=lambda x: (
            x.description is None,
            x.description == "",
            x.description,
            x.name,
        ),
    )

    with open(md, "a+", encoding="utf-8") as md:
        for label in labels:
            # we don't need add top label again
            if label.name in IGNORE_LABELS:
                continue

            issues = get_issues_from_label(repo, label)
            if issues.totalCount:
                md.write("## " + label.name + "\n")
                issues = sorted(issues, key=lambda x: x.created_at, reverse=True)
            i = 0
            for issue in issues:
                if not issue:
                    continue
                if is_me(issue, me):
                    if i == ANCHOR_NUMBER:
                        md.write("<details><summary>显示更多</summary>\n")
                        md.write("\n")
                    add_issue_info(issue, md)
                    i += 1
            if i > ANCHOR_NUMBER:
                md.write("</details>\n")
                md.write("\n")


def get_to_generate_issues(repo, dir_name, issue_number=None):
    md_files = os.listdir(dir_name)
    generated_issues_numbers = [
        int(i.split("_")[0]) for i in md_files if i.split("_")[0].isdigit()
    ]
    to_generate_issues = [
        i
        for i in list(repo.get_issues())
        if int(i.number) not in generated_issues_numbers
    ]
    if issue_number:
        to_generate_issues.append(repo.get_issue(int(issue_number)))
    return to_generate_issues


def ensure_issues_to_generate(repo, issues, issue_numbers):
    issues_by_number = {int(issue.number): issue for issue in issues}
    for issue_number in issue_numbers:
        try:
            issues_by_number[int(issue_number)] = repo.get_issue(int(issue_number))
        except Exception as e:
            print(f"Cannot refresh issue #{issue_number}: {e}")
    return list(issues_by_number.values())


def get_blog_issue_url(issue):
    return f"{BLOG_URL}/#/posts/{issue.number}"


def normalize_content_links(body, repo):
    return body.replace(
        f"https://cdn.jsdelivr.net/gh/{repo.full_name}@main/",
        f"https://cdn.jsdelivr.net/gh/{repo.full_name}@{DEFAULT_BRANCH}/",
    )


def generate_rss_feed(repo, filename, me):
    generator = FeedGenerator()
    generator.id(BLOG_URL)
    generator.title("Couture's Blog")
    generator.author(
        {"name": os.getenv("GITHUB_NAME"), "email": os.getenv("GITHUB_EMAIL")}
    )
    generator.link(href=BLOG_URL)
    generator.link(
        href=f"https://raw.githubusercontent.com/{repo.full_name}/{DEFAULT_BRANCH}/{filename}",
        rel="self",
    )
    for issue in repo.get_issues():
        if not issue.body or not is_me(issue, me) or issue.pull_request:
            continue
        item = generator.add_entry(order="append")
        item.id(get_blog_issue_url(issue))
        item.link(href=get_blog_issue_url(issue))
        item.title(issue.title)
        item.published(issue.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"))
        for label in issue.labels:
            item.category({"term": label.name})
        body = normalize_content_links(issue.body, repo)
        body = "".join(c for c in body if _valid_xml_char_ordinal(c))
        item.content(CDATA(marko.convert(body)), type="html")
    generator.atom_file(filename)


def main(token, repo_name, issue_number=None, dir_name=BACKUP_DIR):
    user = login(token)
    me = get_me(user)
    repo = get_repo(user, repo_name)
    friend_issues, friend_rows = collect_friend_links(repo, me)
    friends_html = render_friends_table(friend_rows)
    sync_friends_issue(friend_issues, friends_html)

    # add to readme one by one, change order here
    add_md_header("README.md", repo_name)
    add_md_friends("README.md", me, friend_issues, friend_rows)
    for func in [add_md_top, add_md_recent, add_md_label, add_md_todo]:
        func(repo, "README.md", me)

    generate_rss_feed(repo, "feed.xml", me)
    to_generate_issues = get_to_generate_issues(repo, dir_name, issue_number)
    to_generate_issues = ensure_issues_to_generate(
        repo, to_generate_issues, [issue.number for issue in friend_issues]
    )

    # save md files to backup folder
    for issue in to_generate_issues:
        save_issue(issue, me, repo, dir_name)


def safe_backup_title(title):
    title = title.replace("/", "-").replace(" ", ".")
    return re.sub(r'[\\:*?"<>|\r\n]+', "-", title).strip(".-") or "untitled"


def remove_old_backup(issue, dir_name):
    prefix = f"{issue.number}_"
    for file_name in os.listdir(dir_name):
        if file_name.startswith(prefix) and file_name.endswith(".md"):
            os.remove(os.path.join(dir_name, file_name))


def save_issue(issue, me, repo, dir_name=BACKUP_DIR):
    remove_old_backup(issue, dir_name)
    md_name = os.path.join(
        dir_name, f"{issue.number}_{safe_backup_title(issue.title)}.md"
    )
    with open(md_name, "w", encoding="utf-8") as f:
        f.write(f"# [{issue.title}]({issue.html_url})\n\n")
        f.write(normalize_content_links(issue.body or "", repo))
        if issue.comments:
            for c in issue.get_comments():
                if is_me(c, me):
                    f.write("\n\n---\n\n")
                    f.write(normalize_content_links(c.body or "", repo))


if __name__ == "__main__":
    if not os.path.exists(BACKUP_DIR):
        os.mkdir(BACKUP_DIR)
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    parser.add_argument(
        "--issue_number", help="issue_number", default=None, required=False
    )
    options = parser.parse_args()
    main(options.github_token, options.repo_name, options.issue_number)
