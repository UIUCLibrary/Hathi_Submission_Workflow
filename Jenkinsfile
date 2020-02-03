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

def get_package_version(stashName, metadataFile){
    ws {
        unstash "${stashName}"
        script{
            def props = readProperties interpolate: true, file: "${metadataFile}"
            deleteDir()
            return props.Version
        }
    }
}

def get_package_name(stashName, metadataFile){
    ws {
        unstash "${stashName}"
        script{
            def props = readProperties interpolate: true, file: "${metadataFile}"
            deleteDir()
            return props.Name
        }
    }
}

pipeline {
    agent none
    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
        timeout(60)  // Timeout after 60 minutes. This shouldn't take this long but it hangs for some reason
        buildDiscarder logRotator(artifactDaysToKeepStr: '30', artifactNumToKeepStr: '30', daysToKeepStr: '100', numToKeepStr: '100')
    }
    environment {
        DEVPI = credentials("DS_devpi")
    }
    triggers {
        parameterizedCron '@daily % DEPLOY_DEVPI=true; TEST_RUN_TOX=true; PACKAGE_CX_FREEZE=true'
    }
    parameters {
        string(name: 'JIRA_ISSUE', defaultValue: "", description: 'Jira task to generate about updates.')
        booleanParam(name: "TEST_RUN_TOX", defaultValue: false, description: "Run Tox Tests")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to DevPi on http://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "PACKAGE_CX_FREEZE", defaultValue: true, description: "Create a package with CX_Freeze")
        string(name: 'URL_SUBFOLDER', defaultValue: "DCCMedusaPackager", description: 'The directory that the docs should be saved under')
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to https://devpi.library.illinois.edu/production/release")
        booleanParam(name: "DEPLOY_DOCS", defaultValue: false, description: "Update online documentation")

    }
    stages {
        stage("Configure"){
            stages{
                stage("Initialize Settings"){
                    parallel{
                        stage("Testing Jira issue"){
                            agent any
                            when {
                                expression {params.JIRA_ISSUE != ""}
                            }
                            options {
                                skipDefaultCheckout(true)
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
                        stage("Getting Distribution Info"){
                            agent {
                                dockerfile {
                                    filename 'CI/docker/python/windows/build/msvc/Dockerfile'
                                    label "windows && docker"
                                }
                            }
                            options{
                                timeout(5)
                            }
                            steps{
                                bat "python setup.py dist_info"
                            }
                            post{
                                success{
                                    stash includes: "hsw.dist-info/**", name: 'DIST-INFO'
                                    archiveArtifacts artifacts: "hsw.dist-info/**"
                                }
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        patterns: [
                                            [pattern: "hsw.dist-info/", type: 'INCLUDE'],
                                            ]
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
        stage("Building") {
            agent {
                dockerfile {
                    filename 'CI/docker/python/windows/build/msvc/Dockerfile'
                    label "windows && docker"
                }
            }
            stages{
                stage("Building Python Package"){
                    steps {
                        bat "python setup.py build -b build "
                    }
                }
                stage("Building Sphinx Documentation"){
                    steps {
                        bat "if not exist logs mkdir logs"
                        bat(
                            label: "Building docs on ${env.NODE_NAME}",
                            script:"python -m sphinx docs/source build/docs/html -d build/docs/.doctrees -w logs\\build_sphinx.log"
                        )
                    }
                    post{
                        always {
                            recordIssues(tools: [sphinxBuild(name: 'Sphinx Documentation Build', pattern: 'logs/build_sphinx.log', id: 'sphinx_build')])
                            archiveArtifacts artifacts: 'logs/build_sphinx.log'
                        }
                        success{
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                            script{
                                unstash "DIST-INFO"
                                def props = readProperties interpolate: true, file: "hsw.dist-info/METADATA"
                                def DOC_ZIP_FILENAME = "${props.Name}-${props.Version}.doc.zip"
                                zip archive: true, dir: "build/docs/html", glob: '', zipFile: "dist/${DOC_ZIP_FILENAME}"
                                stash includes: 'build/docs/html/**', name: 'DOCS_ARCHIVE'
                            }
                        }
                        failure{
                            echo "Failed to build Python package"
                        }
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: 'build/docs', type: 'INCLUDE'],
                                ]
                            )
                        }
                    }
                }
            }
            post{
                cleanup{
                    cleanWs(
                        deleteDirs: true,
                        patterns: [
                            [pattern: 'logs/', type: 'INCLUDE'],
                            [pattern: "dist/", type: 'INCLUDE'],
                            [pattern: "build", type: 'INCLUDE']
                        ]
                    )
                }
            }
        }
        stage("Tests") {
            agent {
                dockerfile {
                    filename 'CI/docker/python/windows/build/msvc/Dockerfile'
                    label "windows && docker"
                }
            }
            stages{
                stage("Setting up Tests"){
                    steps{
                        bat(
                            label: "Creating logging and report directories",
                            script: """
                                if not exist logs mkdir logs
                                if not exist reports mkdir reports
                                if not exist reports\\coverage mkdir reports\\coverage
                                if not exist reports\\doctests mkdir reports\\doctests
                                if not exist reports\\mypy\\html mkdir reports\\mypy\\html
                            """
                        )
                    }
                }
                stage("Run Testing"){
                    parallel {
                        stage("PyTest"){
                            steps{
                                catchError(buildResult: "UNSTABLE", message: 'PyTest found issues', stageResult: "UNSTABLE") {
                                    bat "pytest --junitxml=reports/junit-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:reports/coverage/ --cov=hsw" //  --basetemp={envtmpdir}"
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
                                    junit "reports/junit-pytest.xml"
                                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/coverage', reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                                }
                            }
                        }
                        stage("Doc Test"){
                            steps{
                                bat "python -m sphinx -b doctest docs\\source build\\docs -d build\\docs\\doctrees -v"
                            }
                        }
                        stage("Run MyPy Static Analysis") {
                            steps{
                                catchError(buildResult: "SUCCESS", message: 'MyPy found issues', stageResult: "UNSTABLE") {
                                    bat(
                                        label: "Running Mypy",
                                        script: "mypy -p hsw --html-report reports\\mypy\\html > logs\\mypy.log"
                                    )
                                }
                            }
                            post {
                                always {
                                    archiveArtifacts "logs\\mypy.log"
                                    recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                }
                                cleanup{
                                    cleanWs(patterns: [[pattern: 'logs/mypy.log', type: 'INCLUDE']])
                                }
                            }
                        }
                        stage("Tox") {
                            when {
                                equals expected: true, actual: params.TEST_RUN_TOX
                            }
                            steps {
                                bat (
                                    label: "Run Tox",
                                    script: "tox --workdir .tox -vv  -e py"
                                )
                            }
                            post {
                                always {
                                    archiveArtifacts allowEmptyArchive: true, artifacts: '.tox/py*/log/*.log,.tox/log/*.log,logs/tox_report.json'
                                    recordIssues(tools: [pep8(id: 'tox', name: 'Tox', pattern: '.tox/py*/log/*.log,.tox/log/*.log')])
                                }
                                cleanup{
                                    cleanWs(
                                        patterns: [
                                            [pattern: '.tox/py*/log/*.log', type: 'INCLUDE'],
                                            [pattern: '.tox/log/*.log', type: 'INCLUDE'],
                                            [pattern: 'logs/rox_report.json', type: 'INCLUDE']
                                        ]
                                    )
                                }
                            }
                        }
//                         stage("Run Tox test") {
//                             when{
//                                 equals expected: true, actual: params.TEST_RUN_TOX
//                             }
//                             steps {
//                                 script{
//                                     try{
//                                         bat "tox --parallel=auto --parallel-live --workdir ${WORKSPACE}\\.tox"
//                                     } catch (exc) {
//                                         bat "tox --parallel=auto --parallel-live --workdir ${WORKSPACE}\\.tox --recreate"
//                                     }
//                                 }
//                             }
//                         }
                        stage("Run Flake8 Static Analysis") {
                            steps{
                                catchError(buildResult: "SUCCESS", message: 'Flake8 found issues', stageResult: "UNSTABLE") {
                                    bat "flake8 hsw --format=pylint --tee --output-file=logs\\flake8.log"
                                }
                            }
                            post {
                                always {
                                    recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                                }
                            }
                        }
//                         stage("Run Flake8 Static Analysis") {
//                             steps{
//                                 script{
//                                     try{
//                                         bat "${WORKSPACE}\\venv\\Scripts\\flake8.exe hsw --tee --output-file=${WORKSPACE}\\logs\\flake8.log"
//                                     } catch (exc) {
//                                         echo "flake8 found some warnings"
//                                     }
//                                 }
//                             }
//                             post {
//                                 always {
//                                     stash includes: "logs/flake8.log", name: 'FLAKE8_LOGS'
//                                     node("Windows"){
//                                         checkout scm
//                                         unstash "FLAKE8_LOGS"
//                                         recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
//                                         deleteDir()
//                                     }
//                                 }
//                                 cleanup{
//                                     cleanWs(patterns: [[pattern: 'logs/flake8.log', type: 'INCLUDE']])
//                                 }
//                             }
//                         }
                    }
                }
            }
            post{
                cleanup{
                    cleanWs(
                        deleteDirs: true,
                        patterns: [
                            [pattern: "dist/", type: 'INCLUDE'],
                            [pattern: "reports/", type: 'INCLUDE'],
                            [pattern: 'build/', type: 'INCLUDE'],
                            [pattern: 'logs/', type: 'INCLUDE']
                            ]
                    )
                }
            }
        }
        stage("Packaging") {
            parallel {
                stage("Source and Wheel formats"){
                    agent {
                        dockerfile {
                            filename 'CI/docker/python/windows/build/msvc/Dockerfile'
                            label "windows && docker"
                        }
                    }
                    steps{
                        bat "python setup.py sdist --format zip -d dist bdist_wheel -d dist"
                    }
                    post{
                        success{
                            archiveArtifacts artifacts: "dist/*.whl,dist/*.tar.gz", fingerprint: true
                            stash includes: 'dist/*.whl,dist/*.tar.gz', name: "DIST"
                        }
                        cleanup{
                            cleanWs deleteDirs: true, patterns: [[pattern: 'dist/*.whl,dist/*.zip', type: 'INCLUDE']]
                        }
                    }
                }
                stage("Windows CX_Freeze MSI"){
                    agent {
                        dockerfile {
                            filename 'CI/docker/python/windows/build/msvc/Dockerfile'
                            label "windows && docker"
                        }
                    }
                    when{
                        anyOf{
                            equals expected: true, actual: params.PACKAGE_CX_FREEZE
                        }
                        beforeAgent true
                    }
                    steps{
                        bat "python cx_setup.py bdist_msi --add-to-path=true -k --bdist-dir build/msi -d dist"
                    }
                    post{
                        success{
                            dir("dist") {
                                stash includes: "*.msi", name: "msi"
                            }
                            archiveArtifacts artifacts: "dist/*.msi", fingerprint: true
                        }
                    }
                }
            }
        }
        stage("Deploying to DevPi") {
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                    }
                }
            }
            options{
                timestamps()
            }
            environment{
                PATH = "${WORKSPACE}\\venv\\Scripts;${tool 'CPython-3.6'};${tool 'CPython-3.6'}\\Scripts;${PATH}"
                PKG_VERSION = get_package_version("DIST-INFO", "hsw.dist-info/METADATA")
                PKG_NAME = get_package_name("DIST-INFO", "hsw.dist-info/METADATA")
            }
            stages{
                stage("Install DevPi Client"){
                    steps{
                        bat "pip install devpi-client"
                    }
                }
                stage("Uploading to DevPi staging") {
                    steps {
                        unstash "DIST"
                        unstash "DOCS_ARCHIVE"
                        bat "pip install devpi-client"
                        bat "devpi use https://devpi.library.illinois.edu && devpi login ${env.DEVPI_USR} --password ${env.DEVPI_PSW} && devpi use /${env.DEVPI_USR}/${env.BRANCH_NAME}_staging && devpi upload --from-dir dist"
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
                    parallel {
                        stage("Testing Submitted Source Distribution") {
                            environment {
                                PATH = "${tool 'CPython-3.7'};${tool 'CPython-3.6'};$PATH"
                            }
                            agent {
                                node {
                                    label "Windows && Python3"
                                }
                            }
                            options {
                                skipDefaultCheckout(true)

                            }
                            stages{
                                stage("Creating venv to test sdist"){
                                    steps {
                                        lock("system_python_${NODE_NAME}"){
                                            bat "python -m venv venv"
                                        }
                                        bat "venv\\Scripts\\python.exe -m pip install pip --upgrade && venv\\Scripts\\pip.exe install setuptools --upgrade && venv\\Scripts\\pip.exe install \"tox<3.7\" detox devpi-client"
                                    }

                                }
                                stage("Testing DevPi zip Package"){
                                    options{
                                        timeout(20)
                                    }
                                    environment {
                                        PATH = "${WORKSPACE}\\venv\\Scripts;$PATH"
                                    }
                                    steps {
                                        devpiTest(
                                            devpiExecutable: "${powershell(script: '(Get-Command devpi).path', returnStdout: true).trim()}",
                                            url: "https://devpi.library.illinois.edu",
                                            index: "${env.BRANCH_NAME}_staging",
                                            pkgName: "${env.PKG_NAME}",
                                            pkgVersion: "${env.PKG_VERSION}",
                                            pkgRegex: "zip",
                                            detox: false
                                        )
                                        echo "Finished testing Source Distribution: .zip"
                                    }

                                }
                            }
                            post {
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        disableDeferredWipeout: true,
                                        patterns: [
                                            [pattern: '*tmp', type: 'INCLUDE'],
                                            [pattern: 'certs', type: 'INCLUDE']
                                            ]
                                    )
                                }
                            }

                        }
                        stage("Built Distribution: .whl") {
                            agent {
                                node {
                                    label "Windows && Python3"
                                }
                            }
                            environment {
                                PATH = "${tool 'CPython-3.6'};${tool 'CPython-3.6'}\\Scripts;${tool 'CPython-3.7'};$PATH"
                            }
                            options {
                                skipDefaultCheckout(true)
                            }
                            stages{
                                stage("Creating venv to Test Whl"){
                                    steps {
                                        lock("system_python_${NODE_NAME}"){
                                            bat "if not exist venv\\36 mkdir venv\\36"
                                            bat "\"${tool 'CPython-3.6'}\\python.exe\" -m venv venv\\36"
                                            bat "if not exist venv\\37 mkdir venv\\37"
                                            bat "\"${tool 'CPython-3.7'}\\python.exe\" -m venv venv\\37"
                                        }
                                        bat "venv\\36\\Scripts\\python.exe -m pip install pip --upgrade && venv\\36\\Scripts\\pip.exe install setuptools --upgrade && venv\\36\\Scripts\\pip.exe install \"tox<3.7\" devpi-client"
                                    }

                                }
                                stage("Testing DevPi .whl Package"){
                                    options{
                                        timeout(20)
                                    }
                                    environment {
                                        PATH = "${WORKSPACE}\\venv\\36\\Scripts;${WORKSPACE}\\venv\\37\\Scripts;$PATH"
                                    }
                                    steps {
                                        echo "Testing Whl package in devpi"
                                        devpiTest(
                                                devpiExecutable: "${powershell(script: '(Get-Command devpi).path', returnStdout: true).trim()}",
                                                url: "https://devpi.library.illinois.edu",
                                                index: "${env.BRANCH_NAME}_staging",
                                                pkgName: "${env.PKG_NAME}",
                                                pkgVersion: "${env.PKG_VERSION}",
                                                pkgRegex: "whl",
                                                detox: false
                                            )

                                        echo "Finished testing Built Distribution: .whl"
                                    }
                                }

                            }
                            post {
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        disableDeferredWipeout: true,
                                        patterns: [
                                            [pattern: '*tmp', type: 'INCLUDE'],
                                            [pattern: 'certs', type: 'INCLUDE']
                                            ]
                                    )
                                }
                            }
                        }
                    }


                }
                stage("Deploy to DevPi Production") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            branch "master"
                        }
                    }
                    steps {
                        script {
                            input "Release ${env.PKG_NAME} ${env.PKG_VERSION} to DevPi Production?"
                            bat "venv\\Scripts\\devpi.exe login ${env.DEVPI_USR} --password ${env.DEVPI_PSW} && venv\\Scripts\\devpi.exe use /${env.DEVPI_USR}/${env.BRANCH_NAME}_staging && venv\\Scripts\\devpi.exe push ${env.PKG_NAME}==${env.PKG_VERSION} production/release"
                        }
                    }
                }
            }
            post {
                success {
                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
                    script {
                        bat "venv\\Scripts\\devpi.exe use https://devpi.library.illinois.edu/${env.BRANCH_NAME}_staging && devpi login ${env.DEVPI_USR} --password ${env.DEVPI_PSW} && venv\\Scripts\\devpi.exe use http://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging && venv\\Scripts\\devpi.exe push ${env.PKG_NAME}==${env.PKG_VERSION} DS_Jenkins/${env.BRANCH_NAME}"
                    }
                }
                cleanup{
                    remove_from_devpi("venv\\Scripts\\devpi.exe", "${env.PKG_NAME}", "${env.PKG_VERSION}", "/${env.DEVPI_USR}/${env.BRANCH_NAME}_staging", "${env.DEVPI_USR}", "${env.DEVPI_PSW}")
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
                cleanWs(
                    deleteDirs: true,
                    patterns: [
                        [pattern: 'dist', type: 'INCLUDE'],
                        [pattern: 'build', type: 'INCLUDE'],
                        [pattern: 'reports', type: 'INCLUDE'],
                        [pattern: 'logs', type: 'INCLUDE'],
                        [pattern: 'certs', type: 'INCLUDE'],
                        [pattern: '*tmp', type: 'INCLUDE'],
                        ]
                    )
//            }
        }
    }
}
