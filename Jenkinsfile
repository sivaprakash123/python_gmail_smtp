pipeline {
    agent any

    environment {
        GERRIT_USER = "jenkins"
        GERRIT_HOST = "10.175.2.49"
        GERRIT_PORT = "29418"
        TARGET_BRANCH = "master"
	GERRIT_KEY = "/var/lib/jenkins/.ssh/gerrit_jenkins"
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
                    git push ssh://${GERRIT_USER}@${GERRIT_HOST}:${GERRIT_PORT}/sivaprakash123/python_gmail_smtp.git \
                        HEAD:refs/for/${TARGET_BRANCH}%topic=PR-${CHANGE_ID}
                """
            }
        }

        stage('Check Gerrit Vote') {
            when { changeRequest() }
            steps {
                script {
                    echo "Checking Gerrit vote for Change-ID: ${CHANGE_ID}"

                    def votesJson = sh(
                        script: """
                        ssh -p ${GERRIT_PORT} -i ${GERRIT_KEY} ${GERRIT_USER}@${GERRIT_HOST} \
                        "gerrit query --format=JSON change:${CHANGE_ID} --current-patch-set"
                        """,
                        returnStdout: true
                    ).trim()

                    echo "Gerrit Query Response: ${votesJson}"

                    def vote = sh(
                        script: """
                        echo '${votesJson}' | jq -r '
                          select(.currentPatchSet) |
                          .currentPatchSet.approvals[]? |
                          select(.type==\"Code-Review\") |
                          .value
                        ' | sort -nr | head -1
                        """,
                        returnStdout: true
                    ).trim()

                    if (!vote) {
                        error "❌ No Gerrit vote found — review not completed!"
                    }

                    echo "✅ Gerrit Code-Review Vote = ${vote}"

                    if (vote.toInteger() < 0) {
                        error "❌ Gerrit review failed (vote=${vote}). Rejecting PR."
                    }

                    echo "✅ Gerrit review passed (vote=${vote}) — pipeline can continue"
                }
            }
        }
    }
}

