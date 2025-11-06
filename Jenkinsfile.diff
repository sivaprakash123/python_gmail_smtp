pipeline {
    agent any

    environment {
        GERRIT_USER = "jenkins"
        GERRIT_HOST = "10.175.2.49"
        GERRIT_PORT = "29418"
        TARGET_BRANCH = "master"
        GERRIT_KEY = "/var/lib/jenkins/.ssh/gerrit_jenkins"

        GITHUB_REPO = "sivaprakash123/python_gmail_smtp"
    }

    stages {

        stage('Detect PR') {
            when { changeRequest() }
            steps {
                echo "✅ GitHub PR detected: ID=${env.CHANGE_ID}, Branch=${env.CHANGE_BRANCH}"
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

        stage('Add Gerrit Change-Id if missing') {
            when { changeRequest() }
            steps {
                script {
                    echo "➡️ Checking Change-Id..."

                    // Detect Change-Id
                    def changeId = sh(
                        script: "git log -1 | grep 'Change-Id:' || true",
                        returnStdout: true
                    ).trim()

                    if (!changeId) {
                        echo "⚠️ No Change-Id found — generating one..."

                        sh """
                        git config user.name "Jenkins"
                        git config user.email "jenkins@local"

                        git commit --amend -m "\$(git log -1 --pretty=%B)\n\nChange-Id: I\$(uuidgen | tr -d '-')"
                        """
                    } else {
                        echo "✅ Change-Id exists: ${changeId}"
                    }
                }
            }
        }

        stage('Push to Gerrit for Review') {
            when { changeRequest() }
            steps {
                sh """
                    git remote add gerrit ssh://${GERRIT_USER}@${GERRIT_HOST}:${GERRIT_PORT}/${GITHUB_REPO}.git || true
                    GIT_SSH_COMMAND="ssh -i ${GERRIT_KEY} -o StrictHostKeyChecking=no" \
                    git push gerrit HEAD:refs/for/${TARGET_BRANCH}%topic=PR-${CHANGE_ID}
                """
                echo "📤 Code pushed to Gerrit for review (topic=PR-${CHANGE_ID})"
            }
        }

        // 🔧 PATCHED STAGE BELOW
        stage('Check Gerrit Vote') {
            when { changeRequest() }
            steps {
                script {
                    echo "🔍 Checking Gerrit votes for topic=PR-${CHANGE_ID}..."

                    // Query Gerrit by topic name (maps to GitHub PR ID)
                    def votesJson = sh(
                        script: """
                        ssh -p ${GERRIT_PORT} -i ${GERRIT_KEY} ${GERRIT_USER}@${GERRIT_HOST} \
                        "gerrit query --format=JSON topic:PR-${CHANGE_ID} --current-patch-set"
                        """,
                        returnStdout: true
                    ).trim()

                    echo "📄 Gerrit Response: ${votesJson}"

                    // Extract highest Code-Review vote
                    def vote = sh(
                        script: """
                        echo '${votesJson}' | jq -r '
                          select(.currentPatchSet) |
                          .currentPatchSet.approvals[]? |
                          select(.type=="Code-Review") |
                          .value
                        ' | sort -nr | head -1
                        """,
                        returnStdout: true
                    ).trim()

                    if (!vote) {
                        error "❌ No Gerrit vote yet for PR-${CHANGE_ID}"
                    }

                    echo "✅ Highest Gerrit Code-Review vote = ${vote}"

                    if (vote.toInteger() < 1) {
                        error "❌ Gerrit review not approved (vote=${vote})"
                    }

                    echo "🎉 Gerrit review approved for PR-${CHANGE_ID}"
                }
            }
        }

        stage('Auto Merge GitHub PR After Gerrit Approval') {
            when { changeRequest() }
            steps {
                script {
                    echo "🔁 Gerrit approved — merging GitHub PR"

                    withCredentials([string(credentialsId: 'gerrit-github-token', variable: 'GITHUB_TOKEN')]) {
                        sh """
                        curl -X PUT \
                            -H "Authorization: Bearer ${GITHUB_TOKEN}" \
                            -H "Accept: application/vnd.github.v3+json" \
                            -d '{ "merge_method": "squash" }' \
                            https://api.github.com/repos/${GITHUB_REPO}/pulls/${CHANGE_ID}/merge
                        """
                    }

                    echo "🎉 GitHub PR #${CHANGE_ID} merged"
                }
            }
        }
    }
}

