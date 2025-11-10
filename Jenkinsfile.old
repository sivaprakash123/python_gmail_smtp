pipeline {
    agent any

    environment {
        // === Gerrit settings ===
        GERRIT_USER = "jenkins"
        GERRIT_HOST = "10.175.2.49"
        GERRIT_PORT = "29418"
        TARGET_BRANCH = "master"
        GERRIT_KEY = "/var/lib/jenkins/.ssh/gerrit_jenkins"

        // === GitHub repo details ===
        GITHUB_REPO = "sivaprakash123/python_gmail_smtp"

        // === SonarQube instance (mocked for POC) ===
        SONARQUBE_ENV = "sonarqube-server"

        // === Jira details ===
        JIRA_BASE = "https://karmayogibharat.atlassian.net"
    }

    stages {

        stage('Detect PR') {
 //           when { changeRequest() }
            steps {
                echo "✅ GitHub PR detected: ID=${env.CHANGE_ID}, Branch=${env.CHANGE_BRANCH}"
            }
        }

        stage('Fetch PR Code') {
//            when { changeRequest() }
            steps {
                sh """
                    git fetch origin pull/${CHANGE_ID}/head:pr-${CHANGE_ID}
                    git checkout pr-${CHANGE_ID}
                """
            }
        }

        // ------------------------------------------------------------------
        stage('SonarQube Code Quality Check (Mock for POC)') {
//            when { changeRequest() }
            steps {
        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                script {
                    echo "🧠 [POC MODE] Simulating SonarQube scan..."
                    sh 'echo "Pretending SonarQube scan succeeded..."'
                    echo "✅ [POC MODE] Quality Gate passed (mocked)"
		    currentBuild.result = 'SUCCESS'
                }
	      }
            }
        }
        // ------------------------------------------------------------------

        stage('Add Gerrit Change-Id if missing') {
//            when { changeRequest() }
            steps {
                script {
                    echo "➡️ Checking Change-Id..."
                    def changeId = sh(
                        script: "git log -1 | grep 'Change-Id:' || true",
                        returnStdout: true
                    ).trim()

                    if (!changeId) {
                        echo "⚠️ No Change-Id found — generating one..."
                        sh '''
                            git config user.name "Jenkins"
                            git config user.email "jenkins@local"
                            msg=$(git log -1 --pretty=%B)
                            git commit --amend -m "${msg}\n\nChange-Id: I$(uuidgen | tr -d '-')"
                        '''
                    } else {
                        echo "✅ Change-Id exists: ${changeId}"
                    }
                }
            }
        }

        stage('Push to Gerrit for Review') {
//            when { changeRequest() }
            steps {
                script {
                    echo "📤 Pushing to Gerrit (topic=PR-${CHANGE_ID})"
                    sh """
                        git remote add gerrit ssh://${GERRIT_USER}@${GERRIT_HOST}:${GERRIT_PORT}/${GITHUB_REPO}.git || true
                        GIT_SSH_COMMAND="ssh -i ${GERRIT_KEY} -o StrictHostKeyChecking=no" \
                        git push gerrit HEAD:refs/for/${TARGET_BRANCH}%topic=PR-${CHANGE_ID}
                    """
                }
            }
        }

        stage('Wait for Gerrit +2 / Verified +1') {
            when { changeRequest() }
            steps {
                script {
                    echo "⏳ Waiting for Gerrit approval (topic=PR-${CHANGE_ID})..."
                    timeout(time: 30, unit: 'MINUTES') {
                        waitUntil {
                            def json = sh(
                                script: """
                                    ssh -p ${GERRIT_PORT} -i ${GERRIT_KEY} -o StrictHostKeyChecking=no \
                                    ${GERRIT_USER}@${GERRIT_HOST} \
                                    "gerrit query --format=JSON topic:PR-${CHANGE_ID} --current-patch-set"
                                """,
                                returnStdout: true
                            ).trim()

                            echo "📄 Gerrit Response: ${json}"

                            def codeReview = sh(script: "echo '${json}' | jq -r '.currentPatchSet.approvals[]? | select(.type==\"Code-Review\") | .value' | sort -nr | head -1", returnStdout: true).trim()
                            def verified   = sh(script: "echo '${json}' | jq -r '.currentPatchSet.approvals[]? | select(.type==\"Verified\") | .value' | sort -nr | head -1", returnStdout: true).trim()

                            echo "Code-Review=${codeReview}, Verified=${verified}"
                            return (codeReview == "2" && verified == "1")
                        }
                    }
                    echo "✅ Gerrit approved (+2 / +1)"
                }
            }
        }

        stage('Merge GitHub PR After Gerrit Approval') {
//            when { changeRequest() }
            steps {
                script {
                    echo "🔁 Merging GitHub PR #${CHANGE_ID}"
                    withCredentials([string(credentialsId: 'gerrit-github-token', variable: 'GITHUB_TOKEN')]) {
                        def status = sh(
                            script: """
                                curl -s -o /tmp/merge_resp.json -w "%{http_code}" \
                                  -X PUT \
                                  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
                                  -H "Accept: application/vnd.github.v3+json" \
                                  -d '{ "merge_method": "squash" }' \
                                  https://api.github.com/repos/${GITHUB_REPO}/pulls/${CHANGE_ID}/merge
                            """,
                            returnStdout: true
                        ).trim()
                        if (status != "200") {
                            echo "❌ Merge failed (HTTP ${status}) — see /tmp/merge_resp.json"
                            error("GitHub merge failed.")
                        }
                    }
                    echo "🎉 GitHub PR #${CHANGE_ID} merged successfully"
                }
            }
        }

        stage('Update Jira Ticket') {
//            when { changeRequest() }
            steps {
                script {
                    def jiraKey = sh(
                        script: "git log -1 --pretty=%B | grep -oE '[A-Z]+-[0-9]+' || true",
                        returnStdout: true
                    ).trim()

                    if (jiraKey) {
                        echo "📎 Found Jira ticket ${jiraKey}"
                        withCredentials([usernamePassword(credentialsId: 'jira-api-creds', usernameVariable: 'JIRA_USER', passwordVariable: 'JIRA_TOKEN')]) {
                            def basicAuth = sh(script: "echo -n '${JIRA_USER}:${JIRA_TOKEN}' | base64", returnStdout: true).trim()
                            sh """
                                curl -X POST \
                                    -H "Authorization: Basic ${basicAuth}" \
                                    -H "Content-Type: application/json" \
                                    -d '{ "transition": { "id": "31" } }' \
                                    ${JIRA_BASE}/rest/api/3/issue/${jiraKey}/transitions
                            """
                        }
                        echo "🎯 Jira issue ${jiraKey} moved to next status."
                    } else {
                        echo "⚠️ No Jira key found in commit message."
                    }
                }
            }
        }
    }
}

