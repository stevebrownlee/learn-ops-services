import json, logging, redis, datetime, os
from time import sleep
from github_request import GithubRequest
from slack import SlackAPI

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("TicketMigrator")

github = GithubRequest()

# Initialize the transformer model and Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def format_issue(template_data):
    __location__ = os.path.realpath(os.path.join(
        os.getcwd(), os.path.dirname(__file__)))
    default_template = os.path.join(__location__, 'issue.md')
    return format_from_template(default_template, template_data)

def format_from_template(template_filename, template_data):
    from string import Template
    template_file = open(template_filename, 'r')
    template = Template(template_file.read())
    return template.substitute(template_data)

def migrate_tickets(data):
    """ Process the queries and store the results in Redis """

    # {
    #     'source_repo': project.client_template_url,
    #     'all_target_repositories': issue_target_repos
    # }


    # Get all issues from source repo
    issues = []
    page = 1

    github_url = "https://api.github.com"
    source = data["source_repo"]
    url = f'{github_url}/repos/{source}/issues?state=open&direction=asc'

    while True:
        res = github.get(f'{url}&page={page}')
        new_issues = res.json()
        print(new_issues)
        if not new_issues:
            break
        issues.extend(new_issues)
        page += 1


    issues_to_migrate = []
    for issue in issues:
        new_issue = {}
        new_issue['title'] = issue['title']

        template_data = {}
        template_data['user_name'] = issue['user']['login']
        template_data['user_url'] = issue['user']['html_url']
        template_data['user_avatar'] = issue['user']['avatar_url']
        template_data['date'] = issue['created_at']
        template_data['url'] = issue['html_url']
        template_data['body'] = issue['body']

        new_issue['body'] = format_issue(template_data)
        issues_to_migrate.append(new_issue)


    slack = SlackAPI()
    for target in data['all_target_repositories']:
        messages = []
        url = f'{github_url}/repos/{target}/issues'

        for issue in issues_to_migrate:
            # Pause for 5 seconds between each ticket to prevent Github throttling
            sleep(5)

            try:
                res = github.post(url, issue)
                result_issue = res.json()
            except KeyError as err:
                messages.append(f'Error creating issue {issue["title"]}. {err}.')


        if messages.count() > 0:
            slack.send_message(data['notification_channel'], '\n'.join(messages))
        else:
            slack.send_message(data['notification_channel'], f'All issues migrated successfully to {target}.')

        # Pause for 5 minutes between each migration to prevent Github throttling
        sleep(300)



def main():
    """ Main function that listens for messages on the Redis channel """
    pubsub = redis_client.pubsub()
    pubsub.subscribe('channel_migrate_issue_tickets')
    logger.info('Waiting for messages. To exit press CTRL+C')

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            migrate_tickets(data)

if __name__ == "__main__":
    main()


# PUBLISH channel_migrate_issue_tickets '{ "source_repo": "nss-group-projects/rare-all-issues", "all_target_repositories": ["stevebrownlee/rare-test"], "notification_channel": "C06GHMZB3M3"}'