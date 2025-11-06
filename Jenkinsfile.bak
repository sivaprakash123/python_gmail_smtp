pipeline {
    agent any

    environment {
        GERRIT_USER = "jenkins"
        GERRIT_HOST = "10.175.2.49"
        GERRIT_PORT = "29418"
        TARGET_BRANCH = "gerrit-git-integration"
    }

    stages {

        stage('Detect PR') {
            when { changeRequest() }
            steps {
                script {
                    echo "PR detected: ${env.CHANGE_ID}"
                    echo "Branch: ${env.CHANGE_BRANCH}"
                }
            }
        }

        stage('Fetch PR Code') {
            when { changeRequest() }
            steps {
                sh """
                    git fetch origin pull/${CHANGE_ID}/head:pr-${CHANGE_ID}
                    git checkout pr-${CHANGE_ID}
                """
            }
        }

        stage('Push to Gerrit for Review') {
            when { changeRequest() }
            steps {
                sh """
                    git push ssh://${GERRIT_USER}@${GERRIT_HOST}:${GERRIT_PORT}/your/repo.git \
                        HEAD:refs/for/${TARGET_BRANCH}%topic=PR-${CHANGE_ID}
                """
            }
        }
    }
}
