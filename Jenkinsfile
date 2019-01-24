#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*

@Library(["devpi", "PythonHelpers"]) _

def remove_from_devpi(devpiExecutable, pkgName, pkgVersion, devpiIndex, devpiUsername, devpiPassword){
    script {
                try {
                    bat "${devpiExecutable} login ${devpiUsername} --password ${devpiPassword}"
                    bat "${devpiExecutable} use ${devpiIndex}"
                    bat "${devpiExecutable} remove -y ${pkgName}==${pkgVersion}"
                } catch (Exception ex) {
                    echo "Failed to remove ${pkgName}==${pkgVersion} from ${devpiIndex}"
            }

    }
}



// TODO: replace global vars with env vars


pipeline {
    agent {
        label "Windows && Python3"
    }
    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
        timeout(60)  // Timeout after 60 minutes. This shouldn't take this long but it hangs for some reason
        checkoutToSubdirectory("source")
    }
    triggers {
        cron('@daily')
    }
    environment {
        PATH = "${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
        PKG_NAME = pythonPackageName(toolName: "CPython-3.6")
        PKG_VERSION = pythonPackageVersion(toolName: "CPython-3.6")
        DOC_ZIP_FILENAME = "${env.PKG_NAME}-${env.PKG_VERSION}.doc.zip"
        DEVPI = credentials("DS_devpi")
    }
    parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        string(name: 'JIRA_ISSUE', defaultValue: "", description: 'Jira task to generate about updates.')
        booleanParam(name: "BUILD_DOCS", defaultValue: true, description: "Build documentation")
        booleanParam(name: "TEST_RUN_DOCTEST", defaultValue: true, description: "Test documentation")
        booleanParam(name: "TEST_RUN_PYTEST", defaultValue: true, description: "Run unit tests with PyTest")
        booleanParam(name: "TEST_RUN_MYPY", defaultValue: true, description: "Run MyPy static analysis")
        booleanParam(name: "TEST_RUN_TOX", defaultValue: true, description: "Run Tox Tests")
        booleanParam(name: "TEST_RUN_FLAKE8", defaultValue: true, description: "Run Flake8 static analysis")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to DevPi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        string(name: 'URL_SUBFOLDER', defaultValue: "DCCMedusaPackager", description: 'The directory that the docs should be saved under')
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to https://devpi.library.illinois.edu/production/release")
        booleanParam(name: "DEPLOY_DOCS", defaultValue: false, description: "Update online documentation")

    }
    stages {
        stage("Configure"){
            stages{
                stage("Purge all existing data in workspace"){
                    when{
                        equals expected: true, actual: params.FRESH_WORKSPACE
                    }
                    steps{
                        deleteDir()
                        dir("source"){
                            checkout scm
                        }
                    }
                }

                stage("Testing Jira issue"){
                    agent any
                    when {
                        expression {params.JIRA_ISSUE != ""}
                    }
                    steps {
                        echo "Finding Jira issue $params.JIRA_ISSUE"
                        script {
                            // def result = jiraSearch "issue = $params.JIRA_ISSUE"
                            def result = jiraIssueSelector(issueSelector: [$class: 'JqlIssueSelector', jql: "issue = $params.JIRA_ISSUE"])
                            if(result.isEmpty()){
                                echo "Jira issue $params.JIRA_ISSUE not found"
                                error("Jira issue $params.JIRA_ISSUE not found")

                            } else {
                                echo "Located ${result}"
                            }
                        }

                    }
                }
//                stage("Cleanup"){
//                    steps {
//
//
//                        dir("logs"){
//                            deleteDir()
//                            echo "Cleaned out logs directory"
//                            bat "dir"
//                        }
//
//                        dir("build"){
//                            deleteDir()
//                            echo "Cleaned out build directory"
//                            bat "dir"
//                        }
//                        dir("dist"){
//                            deleteDir()
//                            echo "Cleaned out dist directory"
//                            bat "dir"
//                        }
//
//                        dir("reports"){
//                            deleteDir()
//                            echo "Cleaned out reports directory"
//                            bat "dir"
//                        }
//                    }
//                    post{
//                        failure {
//                            deleteDir()
//                        }
//                    }
//                }
                stage("Installing required system level dependencies"){
                    steps{
                        lock("system_python_${NODE_NAME}"){
                            bat "python -m pip install --upgrade pip --quiet"
                        }
                    }
                    post{
                        always{
                            lock("system_python_${NODE_NAME}"){
                                bat "(if not exist logs mkdir logs) && python -m pip list > logs\\pippackages_system_${NODE_NAME}.log"
                            }
                            archiveArtifacts artifacts: "logs/pippackages_system_${NODE_NAME}.log"
                        }
                        failure {
                            deleteDir()
                        }
                    }
                }
                stage("Creating virtualenv for building"){
                    steps{
                        bat "python -m venv venv"
                        script {
                            try {
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip"
                            }
                            catch (exc) {
                                bat "python -m venv venv"
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
                            }
                        }
                        bat "venv\\Scripts\\pip.exe install -U setuptools"
//                        TODO: when detox is fixed, just use the most recent version
                        bat "venv\\Scripts\\pip.exe install devpi-client pytest pytest-cov lxml -r source\\requirements.txt -r source\\requirements-dev.txt --upgrade-strategy only-if-needed"
                        bat "venv\\Scripts\\pip.exe install detox==0.13 tox==3.2.1"
                    }
                    post{
                        success{
                            bat "venv\\Scripts\\pip.exe list > ${WORKSPACE}\\logs\\pippackages_venv_${NODE_NAME}.log"
                            archiveArtifacts artifacts: "logs/pippackages_venv_${NODE_NAME}.log"
                        }
                    }
                }
            }
            post{
                success{
                    echo "Configured ${env.PKG_NAME}, version ${env.PKG_VERSION}, for testing."
                }
                failure{
                    deleteDir()
                }
            }
        }

        stage("Building") {
            stages{
                stage("Building Python Package"){
                    steps {


                        dir("source"){
                            powershell "& ${WORKSPACE}\\venv\\Scripts\\python.exe setup.py build -b ${WORKSPACE}\\build  | tee ${WORKSPACE}\\logs\\build.log"
                        }

                    }
                    post{
                        always{
                            warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'logs/build.log']]
                            archiveArtifacts artifacts: "logs/build.log"
                        }
                        failure{
                            echo "Failed to build Python package"
                        }
                    }
                }
                stage("Building Sphinx Documentation"){
                    steps {
                        echo "Building docs on ${env.NODE_NAME}"
                        dir("source"){
                            powershell "& ${WORKSPACE}\\venv\\Scripts\\python.exe setup.py build_sphinx --build-dir ${WORKSPACE}\\build\\docs | tee ${WORKSPACE}\\logs\\build_sphinx.log"
                        }
                    }
                    post{
                        always {
                            warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'logs/build_sphinx.log']]
                            archiveArtifacts artifacts: 'logs/build_sphinx.log'
                        }
                        success{
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                            zip archive: true, dir: "build/docs/html", glob: '', zipFile: "dist/${env.DOC_ZIP_FILENAME}"
                            stash includes: 'build/docs/html/**', name: 'docs'
                        }
                        failure{
                            echo "Failed to build Python package"
                        }
                    }
                }
            }
        }
        stage("Tests") {
            parallel {
                stage("PyTest"){
                    when {
                        equals expected: true, actual: params.TEST_RUN_PYTEST
                    }
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\Scripts\\pytest.exe --junitxml=../reports/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:${WORKSPACE}/reports/coverage/ --cov=hsw" //  --basetemp={envtmpdir}"
                        }

                    }
                    post {
                        always{
                            dir("reports"){
                                script{
                                    def report_files = findFiles glob: '**/*.pytest.xml'
                                    report_files.each { report_file ->
                                        echo "Found ${report_file}"
                                        // archiveArtifacts artifacts: "${log_file}"
                                        junit "${report_file}"
                                        bat "del ${report_file}"
                                    }
                                }
                            }
                            // junit "reports/junit-${env.NODE_NAME}-pytest.xml"
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/coverage', reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                        }
                    }
                }
                stage("Doc Test"){
                    when{
                        equals expected: true, actual: params.TEST_RUN_DOCTEST
                    }
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe -b doctest docs\\source ${WORKSPACE}\\build\\docs -d ${WORKSPACE}\\build\\docs\\doctrees -v"
                        }
                    }

                }
                stage("Run MyPy Static Analysis") {
                    when {
                        equals expected: true, actual: params.TEST_RUN_MYPY
                    }
                    steps{
                        script{
                            try{
                                dir("source"){
                                    powershell "& ${WORKSPACE}\\venv\\Scripts\\mypy.exe -p hsw --html-report ${WORKSPACE}\\reports\\mypy\\html | tee ${WORKSPACE}\\logs\\mypy.log"
                                }
//                                }
                            } catch (exc) {
                                echo "MyPy found some warnings"
                            }

                        }
                    }
                    post {
                        always {
                            archiveArtifacts "logs\\mypy.log"
                            warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MyPy', pattern: 'logs/mypy.log']], unHealthy: ''
                            publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                        }
                        cleanup{
                            cleanWs(patterns: [[pattern: 'logs/mypy.log', type: 'INCLUDE']])
                        }
                    }
                }
                stage("Run Tox test") {
                    when{
                        equals expected: true, actual: params.TEST_RUN_TOX
                    }
                    steps {
                        dir("source"){
                            script{
                                try{
                                    bat "${WORKSPACE}\\venv\\Scripts\\tox.exe --workdir ${WORKSPACE}\\.tox"
                                } catch (exc) {
                                    bat "${WORKSPACE}\\venv\\Scripts\\tox.exe --workdir ${WORKSPACE}\\.tox --recreate"
                                }
                            }

                        }
                    }
                }
                stage("Run Flake8 Static Analysis") {
                    when {
                        equals expected: true, actual: params.TEST_RUN_FLAKE8
                    }
                    steps{
                        script{
                            try{
                                dir("source"){
                                    bat "${WORKSPACE}\\venv\\Scripts\\flake8.exe hsw --format=pylint --tee --output-file=${WORKSPACE}\\logs\\flake8.log"
                                }
                            } catch (exc) {
                                echo "flake8 found some warnings"
                            }
                        }
                    }
                    post {
                        always {
                            script{
                                try{
                                    recordIssues(tools: [[name: 'Flake8', pattern: 'logs/flake8.log', tool: pyLint()]])
                                } catch(exc){
                                    echo "Failed to use recordIssues command. Falling back to warnings command. Reason: ${exc}"
                                    warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'PyLint', pattern: 'logs/flake8.log']], unHealthy: ''
                                }
                            }

                        }
                        cleanup{
                            cleanWs(patterns: [[pattern: 'logs/flake8.log', type: 'INCLUDE']])
                        }
                    }
                }
            }
        }
        stage("Packaging") {
            when {
                expression { params.DEPLOY_DEVPI == true || params.RELEASE != "None"}
            }
            parallel {
                stage("Source and Wheel formats"){
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\scripts\\python.exe setup.py sdist -d ${WORKSPACE}\\dist bdist_wheel -d ${WORKSPACE}\\dist"
                        }

                    }
                    post{
                        success{
                            dir("dist"){
                                archiveArtifacts artifacts: "*.whl", fingerprint: true
                                archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
                            }
                        }
                    }
                }
                stage("Windows CX_Freeze MSI"){
                    agent{
                        node {
                            label "Windows"
                        }
                    }
                    options {
                        skipDefaultCheckout true
                    }
                    steps{
                        bat "dir"
                        deleteDir()
                        bat "dir"
                        checkout scm
                        bat "dir /s / B"
                        bat "${tool 'CPython-3.6'}\\python -m venv venv"
                        bat "venv\\Scripts\\python.exe -m pip install -U pip>=18.0"
                        bat "venv\\Scripts\\pip.exe install -U setuptools"
                        bat "venv\\Scripts\\pip.exe install cx_freeze appdirs"
                        bat "venv\\Scripts\\pip.exe install -r requirements.txt -r requirements-dev.txt"
                        bat "venv\\Scripts\\python.exe cx_setup.py bdist_msi --add-to-path=true -k --bdist-dir build/msi"
                        // bat "make freeze"


                    }
                    post{
                        success{
                            dir("dist") {
                                stash includes: "*.msi", name: "msi"
                                archiveArtifacts artifacts: "*.msi", fingerprint: true
                            }
                        }
                        cleanup{
                            bat "dir"
                            deleteDir()
                            bat "dir"
                        }
                    }
                }
            }
        }
//        TODO: make devpi a seq stage
        stage("Deploying to DevPi staging") {
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                    }
                }
            }
            steps {
                bat "venv\\Scripts\\devpi.exe use http://devpy.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                    script {
                        bat "venv\\Scripts\\devpi.exe upload --from-dir dist"
                        try {
//                            bat "venv\\Scripts\\devpi.exe upload --only-docs"
                            bat "venv\\Scripts\\devpi.exe upload --only-docs ${WORKSPACE}\\dist\\${env.DOC_ZIP_FILENAME}"
                        } catch (exc) {
                            echo "Unable to upload to devpi with docs."
                        }
                    }
                }

            }
        }
        stage("Test Devpi packages") {
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                    }
                }
            }
//            steps {
            parallel {
                stage("Source Distribution: .tar.gz") {
                    steps {
                        devpiTest(
                                devpiExecutable: "venv\\Scripts\\devpi.exe",
                                url: "https://devpi.library.illinois.edu",
                                index: "${env.BRANCH_NAME}_staging",
                                pkgName: "${env.PKG_NAME}",
                                pkgVersion: "${env.PKG_VERSION}",
                                pkgRegex: "tar.gz",
                                detox: true
                            )
                    }
                    post {
                        failure {
                            echo "Tests for .tar.gz source on DevPi failed."
                        }
                    }

                }
//                stage("Source Distribution: .tar.gz") {
//                    steps {
//                        echo "Testing Source tar.gz package in DevPi"
//                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
//                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
//
//                        }
//                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
//
//                        script {
//                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${env.PKG_NAME} -s tar.gz  --verbose"
//                            if(devpi_test_return_code != 0){
//                                error "Devpi exit code for tar.gz was ${devpi_test_return_code}"
//                            }
//                        }
//                        echo "Finished testing Source Distribution: .tar.gz"
//                    }
//                    post {
//                        failure {
//                            echo "Tests for .tar.gz source on DevPi failed."
//                        }
//                    }
//
//                }
//                stage("Built Distribution: .whl") {
//                    agent {
//                        node {
//                            label "Windows && Python3"
//                        }
//                    }
//                    options {
//                        skipDefaultCheckout()
//                    }
//                    steps {
//                        echo "Testing Whl package in devpi"
//                        bat "${tool 'CPython-3.6'} -m venv venv"
//                        bat "venv\\Scripts\\pip.exe install tox devpi-client"
//                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
//                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
//                        }
//                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
//                        script{
//                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${env.PKG_NAME} -s whl  --verbose"
//                            if(devpi_test_return_code != 0){
//                                error "Devpi exit code for whl was ${devpi_test_return_code}"
//                            }
//                        }
//                        echo "Finished testing Built Distribution: .whl"
//                    }
//                    post {
//                        failure {
//                            echo "Tests for whl on DevPi failed."
//                        }
//                    }
//                }
            stage("Built Distribution: .whl") {
                    agent {
                        node {
                            label "Windows && Python3"
                        }
                    }
                    options {
                        skipDefaultCheckout()
                    }
                    steps {
                        echo "Testing Whl package in DevPi"
                        bat "${tool 'CPython-3.6'}\\python -m venv venv"
                        bat "venv\\Scripts\\python.exe -m pip install -U pip"
                        bat "venv\\Scripts\\pip.exe install detox==0.13 tox==3.2.1 devpi-client"
                        bat "venv\\Scripts\\pip.exe install -U setuptools"
                        devpiTest(
                                devpiExecutable: "venv\\Scripts\\devpi.exe",
                                url: "https://devpi.library.illinois.edu",
                                index: "${env.BRANCH_NAME}_staging",
                                pkgName: "${env.PKG_NAME}",
                                pkgVersion: "${env.PKG_VERSION}",
                                pkgRegex: "whl",
                                detox: true
                            )
                    }
                    post {
                        failure {
                            echo "Tests for whl on DevPi failed."
                        }
                    }
                }
            }

            post {
                success {
                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
                    script {
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "venv\\Scripts\\devpi.exe push ${env.PKG_NAME}==${env.PKG_VERSION} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                        }
                    }
                }
            }
        }
        stage("Deploy"){
            parallel {
                stage("Deploy Online Documentation") {
                    when{
                        equals expected: true, actual: params.DEPLOY_DOCS
                    }
                    steps{
                        dir("build/docs/html/"){
                            input 'Update project documentation?'
                            sshPublisher(
                                publishers: [
                                    sshPublisherDesc(
                                        configName: 'apache-ns - lib-dccuser-updater',
                                        sshLabel: [label: 'Linux'],
                                        transfers: [sshTransfer(excludes: '',
                                        execCommand: '',
                                        execTimeout: 120000,
                                        flatten: false,
                                        makeEmptyDirs: false,
                                        noDefaultExcludes: false,
                                        patternSeparator: '[, ]+',
                                        remoteDirectory: "${params.DEPLOY_DOCS_URL_SUBFOLDER}",
                                        remoteDirectorySDF: false,
                                        removePrefix: '',
                                        sourceFiles: '**')],
                                    usePromotionTimestamp: false,
                                    useWorkspaceInPromotion: false,
                                    verbose: true
                                    )
                                ]
                            )
                        }
                    }
                }
                stage("Deploy standalone to Hathi tools Beta"){
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_HATHI_TOOL_BETA
                            equals expected: true, actual: params.PACKAGE_WINDOWS_STANDALONE
                        }
                    }
                    steps {
                        unstash "standalone_installer"
                        input 'Update standalone to //storage.library.illinois.edu/HathiTrust/Tools/beta/?'
                        cifsPublisher(
                                    publishers: [[
                                        configName: 'hathitrust tools',
                                        transfers: [[
                                            cleanRemote: false,
                                            excludes: '',
                                            flatten: false,
                                            makeEmptyDirs: false,
                                            noDefaultExcludes: false,
                                            patternSeparator: '[, ]+',
                                            remoteDirectory: 'beta',
                                            remoteDirectorySDF: false,
                                            removePrefix: '',
                                            sourceFiles: '*.msi'
                                            ]],
                                        usePromotionTimestamp: false,
                                        useWorkspaceInPromotion: false,
                                        verbose: false
                                        ]]
                                )
                    }
                }
                stage("Deploy to DevPi Production") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            equals expected: true, actual: params.DEPLOY_DEVPI
                            branch "master"
                        }
                    }
                    steps {
                        script {
                            // def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                            // def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                            input "Release ${env.PKG_NAME} ${env.PKG_VERSION} to DevPi Production?"
                            withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                bat "venv\\Scripts\\devpi.exe push ${env.PKG_NAME}==${env.PKG_VERSION} production/release"
                            }
                        }
                    }
                }
                stage("Deploy Standalone Build to SCCM") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_SCCM
                            equals expected: true, actual: params.PACKAGE_WINDOWS_STANDALONE
                            branch "master"
                        }
                        // expression { params.RELEASE == "Release_to_devpi_and_sccm"}
                    }

                    steps {
                        unstash "msi"
                        unstash "Deployment"
                        script{
                            // def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                            def msi_files = findFiles glob: '*.msi'

                            def deployment_request = requestDeploy yaml: "deployment.yml", file_name: msi_files[0]
                            cifsPublisher(
                                publishers: [[
                                    configName: 'SCCM Staging',
                                    transfers: [[
                                        cleanRemote: false,
                                        excludes: '',
                                        flatten: false,
                                        makeEmptyDirs: false,
                                        noDefaultExcludes: false,
                                        patternSeparator: '[, ]+',
                                        remoteDirectory: '',
                                        remoteDirectorySDF: false,
                                        removePrefix: '',
                                        sourceFiles: '*.msi'
                                        ]],
                                    usePromotionTimestamp: false,
                                    useWorkspaceInPromotion: false,
                                    verbose: false
                                    ]]
                                )

                            // deployStash("msi", "${env.SCCM_STAGING_FOLDER}/${name}/")

                            input("Deploy to production?")
                            writeFile file: "deployment_request.txt", text: deployment_request
                            echo deployment_request
                            cifsPublisher(
                                publishers: [[
                                    configName: 'SCCM Upload',
                                    transfers: [[
                                        cleanRemote: false,
                                        excludes: '',
                                        flatten: false,
                                        makeEmptyDirs: false,
                                        noDefaultExcludes: false,
                                        patternSeparator: '[, ]+',
                                        remoteDirectory: '',
                                        remoteDirectorySDF: false,
                                        removePrefix: '',
                                        sourceFiles: '*.msi'
                                        ]],
                                    usePromotionTimestamp: false,
                                    useWorkspaceInPromotion: false,
                                    verbose: false
                                    ]]
                            )
                            // deployStash("msi", "${env.SCCM_UPLOAD_FOLDER}")
                        }
                    }
                    post {
                        success {
                            archiveArtifacts artifacts: "deployment_request.txt"
                        }
                    }
                }
            }
        }
    }
     post {
        cleanup{
            script {
                if(fileExists('source/setup.py')){
                    dir("source"){
                        try{
                            retry(3) {
                                bat "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py clean --all"
                            }
                        } catch (Exception ex) {
                            echo "Unable to successfully run clean. Purging source directory."
                            deleteDir()
                        }
                    }
                }
                bat "dir"
                if (env.BRANCH_NAME == "master" || env.BRANCH_NAME == "dev"){
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "venv\\Scripts\\devpi.exe login DS_Jenkins --password ${DEVPI_PASSWORD}"
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                    }

                    def devpi_remove_return_code = bat returnStatus: true, script:"venv\\Scripts\\devpi.exe remove -y ${env.PKG_NAME}==${env.PKG_VERSION}"
                    echo "Devpi remove exited with code ${devpi_remove_return_code}."
                }
            }
        }
    }
}
