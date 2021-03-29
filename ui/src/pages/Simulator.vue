<template>
  <div id="debugger" class="container-fluid">
      <header class="navbar navbar-inverse row">
          <div class="col-1">
            <a class="navbar-brand" href="/admin" target="_blank">
              <img id="logo" src="@/assets/logo.png"/>{{title}}
            </a>
          </div>
          <div class="col-1">
              <label class="switch">
                  <input type="checkbox" checked>
                  <span class="slider round" id="toggle-layout"></span>
              </label>
          </div>
          <div class="col-9 text-center" id="workflow">
              <input v-model="workflowName"/>
              <span>.</span>
              <input v-model="workflowVersion"/>
          </div>
          <div class="col-1" v-on:click="reloadWorkflow">
              <v-icon id="reload" name="circle-notch"></v-icon>
          </div>
      </header>
      <main class="main row">
          <div class="col-3 sidebar api-input-wrapper">
              <h2>api input</h2>
              <div class="content">
                  <h3>Browser</h3>
                  <p>
                      <label>session id</label>
                      <input type="text" name="session_id" v-model="sessionId" placeholder=""/>
                  </p>
                  <h3>Organization</h3>
                  <p>
                      <label>app id:</label>
                      <input type="text" name="app_id" v-model="appId" placeholder="App ID"/>
                  </p>
                  <h3>user info:</h3>
                  <p>
                      <label>chatbot user id:</label>
                      <input type="text" name="user_id" v-model="userId" placeholder="Astound"/>
                  </p>
                  <p>
                      <label>first name:</label>
                      <input type="text" name="first_name" v-model="firstName" placeholder="Astound"/>
                  </p>
                  <p>
                      <label>Country:</label>
                      <table>
                          <tr><td><input type="radio" name="germany" value="Germany" v-model="country"></td><td>Germany</td></tr>
                          <tr><td><input type="radio" name="usa" value="United States of America" v-model="country"></td><td>United States of America</td></tr>
                          <tr><td>Or type it here: </td><td><input type="text" name="other_country" v-model="country"/></td></tr>
                      </table>
                  </p>
                  <p>
                      <label>company:</label>
                      <input type="text" name="country" v-model="company" placeholder="Adidas AG"/>
                  </p>
                  <p>
                      <label>group:</label>
                      <input type="text" name="country" v-model="group" placeholder=""/>
                  </p>
                  <h3>incidence</h3>
                  <p>
                      <label>servicenow instance name:</label>
                      <input type="text" name="instance_name" v-model="instanceName"
                            placeholder="ServiceNow Instance Name"
                      />
                  </p>
              </div>
          </div>
          <div class="col-7 dialog-wrapper">
              <div id="dialog" class="dialog">
                <div v-for="(message, index) in messageList" :key="index">
                  <div v-if="message.debug" class="debug-wrapper">
                    <debug-message v-bind:message="message"></debug-message>
                  </div>
                  <div v-else-if="message.me" v-cloak class="message-wrapper me">
                    <div class="circle-wrapper animated bounceIn">
                      <img src="@/assets/user-man.png" alt=""/>
                    </div>
                    <div v-cloak class="text-wrapper animated fadeIn">
                      <div class="timestamp">{{ message.timestamp | moment("MMMM Do, YYYY hh:mm:ss") }}</div>
                      <div v-html="message.message"></div>
                    </div>
                  </div>
                  <div v-else-if="message.them" v-cloak class="message-wrapper them">
                    <div class="circle-wrapper animated bounceIn">
                      <img src="@/assets/bot-girl.png" alt=""/>
                    </div>
                    <answer class="text-wrapper" :message="message" v-on:clickToMessage="clickToMessage"></answer>
                  </div>
                </div>
                <loading v-if="loading"></loading>
              </div>
              <div class="bottom col-12" id="bottom">
                <input id="input" class="input" v-on:keyup.enter="sendMessage" v-model="inputMessage" placeholder="" />
                <span v-on:click="sendMessage">
                  <v-icon class="send" name="arrow-circle-right"></v-icon>
                </span>
              </div>
          </div>
          <div class="col-2 sidebar logging-wrapper" id="logging">
              <h2>Workflow States</h2>
              <div class="content">
                  <span v-for="(state, index) in stateHistory" :key="index">
                      <v-icon name="arrow-right"></v-icon>
                      <span v-cloak class="state">{{ state }}</span>
                  </span>
              </div>
          </div>
      </main>
  </div>
</template>

<script>
import Answer from '@/pages/Answer'
import { illusionistAPI } from '@/utils/rest-config'

const uuidv4 = require('uuid/v4')

export default {
  name: 'Simulator',
  components: {
    'answer': Answer
  },
  data: function () {
    return {
      title: 'Simulater',
      inputMessage: null,
      url: null,
      me: null,
      appId: this.$route.params.appId || 1,
      instanceName: 'ven01702',
      messageList: [],
      stateHistory: [],
      clientId: 'simulator',
      sessionId: '',
      virtualAgentUserId: 'virtual_agent',
      userId: 'neva_test_user',
      firstName: 'Virtual Agent',
      country: 'Germany',
      company: 'adidas AG',
      group: 'adidas_incident_manager',
      loading: false
    }
  },
  computed: {
    askApiPath: function () {
      const vm = this
      var apiPath = '/api/1/debug'
      if (vm.sessionId === '') {
        vm.sessionId = uuidv4()
      }
      apiPath += '?session_id=' + vm.sessionId
      return apiPath
    }
  },
  mounted: function () {
    document.getElementById('input').focus()
  },
  watch: {
    'messageList': function () {
      this.scrollBottom()
    },
    'workflowVersion': function (value) {
      this.$router.push({
        name: 'Simulator',
        params: {
          'workflow': this.workflowName,
          'version': value.toString(),
          'appId': this.appId
        }
      })
    },
    appId: function (value) {
      this.$router.push(value.toString())
    }
  },
  methods: {
    reloadWorkflow () {
      console.log('Reload workflow.')
      const apiPath = '/api/1/reload'
      this.sessionId = null
      illusionistAPI
        .post(apiPath, {
          name: this.workflowName,
          version: this.workflowVersion
        })
        .then((response) => {
          this.messageList = []
        })
        .catch(err => {
          console.error(err)
        })
    },
    processMessage (response) {
      this.messageList.push({
        message: response,
        me: false,
        them: true,
        uuid: response.uuid,
        timestamp: new Date()
      })
    },
    sendMessage () {
      var vm = this
      console.log('Waiting for reply...')
      if (vm.inputMessage === '') {
        return
      }
      vm.messageList.push({
        message: vm.inputMessage,
        me: true,
        them: false,
        timestamp: new Date()
      })

      const payload = {
        utterance: vm.inputMessage,
        workflow: vm.workflowName + '.' + vm.workflowVersion,
        virtual_agent_user_id: vm.virtualAgentUserId,
        client_id: vm.clientId,
        app_id: vm.appId,
        instance_name: vm.instanceName,
        user_id: vm.userId,
        user_info: {
          first_name: vm.firstName,
          country: vm.country,
          company: vm.company,
          group: vm.group
        },
        debug: true
      }

      vm.loading = true
      illusionistAPI
        .post(vm.apiPath, payload)
        .then((response) => {
          const states = response.data.payloads.state_history
          const answer = response.data.payloads.answer
          vm.sessionId = response.data.session_id
          vm.processMessage(answer)
          vm.setStateHistory(states)
        })
        .catch((e) => {
          const answer = { 'pretext': vm.bot.params.answer_error }
          vm.processMessage(answer)
        })
        .then(() => {
          vm.loading = false
        })

      vm.inputMessage = ''
      document.getElementById('input').focus()
    },
    clickToMessage (message) {
      this.inputMessage = message
      this.sendMessage()
    },
    setStateHistory (states) {
      this.stateHistory = states
    },
    sendDebugging (debugInfo) {
      let str = ''
      Object.keys(debugInfo).forEach(key => {
        str = str + key + ' : ' + JSON.stringify(debugInfo[ key ], null, 4) + '\n'
      })
      this.messageList.push({
        message: str,
        me: false,
        them: false,
        debug: true
      })
    },

    scrollBottom () {
      setTimeout(() => {
        const $dialog = document.getElementById('dialog')
        document.getElementById('dialog').scrollTop = $dialog.scrollHeight + 10
      }, 1)
    }
  }
}
</script>

<style lang="sass" scoped>
@import '@/assets/action.sass';

li
  list-style: none;

textarea, input
  border: 1px solid $color-g4;
  border-radius: $border-radius-s;
  outline: none;
  padding: 0.3em 0.5em;

label
  margin: 0;

button
  cursor: pointer;

h2, h3, h4
  text-transform: capitalize;
  font-weight: bold;
  margin: 1em 0;

h2
  font-size: 1.35em;
  padding-bottom: 1em;

h3
  font-size: 1.15em;

h4
  font-size: 1.1em;

.col-0
  width: 0;

*:focus
  outline-color: transparent;
  outline-style: none;
  -webkit-tap-highlight-color: transparent;

*::-webkit-scrollbar
  width: 0px;
  background: transparent;

*::-webkit-scrollbar-thumb
  background: #999;

.inner
  position: relative;
  height: 100%;
  width: 100%;

[v-cloak]
  display: none;

body
  background-color: $color-white;
  font-family: 'Noto Sans', sans-serif;
  font-style: normal;
  height: 100vh;

@media (min-width: 1200px)
  .container
    max-width: 90%;

/* layers */
#debugger
  opacity: 1;

#workflow-viewer
  z-index: -1;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: none;

#workflow-viewer img
  width: 100%;
  height: 100%;

/* 1. debugger layer */
/* header */
header.navbar
  background: $color-g2;
  font-size: 0.8em;
  line-height: 1em;
  height: 50px;
  text-align: left;
  border: none;
  input
    background-color: $color-white;

#reload
  color: $color-c4;
  height: 30px;
  width: 30px;
  float: right;
  cursor: pointer;

.navbar .options
  height: 32px;
  width: 32px;
  cursor: pointer;

/* The switch button for sidebar toggle */
.switch
  position: relative;
  display: inline-block;
  vertical-align: middle;
  width: 60px;
  height: 34px;
  input
    display: none;

.slider
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: $color-g3;
  -webkit-transition: .4s;
  transition: .4s;
  &.round
    border-radius: 34px;
    &:before
      border-radius: 50%;
      position: absolute;
      content: "";
      height: 26px;
      width: 26px;
      left: 4px;
      bottom: 4px;
      background-color: white;
      -webkit-transition: .4s;
      transition: .4s;

input:checked + .slider
  background-color: $color-c4;

input:focus + .slider
  box-shadow: $box-shadow;

input:checked + .slider:before
  -webkit-transform: translateX(26px);
  -ms-transform: translateX(26px);
  transform: translateX(26px);

/* layout */
.main
  position: relative;
  height: -webkit-calc(100vh - 8rem);
  height: calc(100vh - 3rem);
  overflow: auto;
  .navbar
    background: $color-g2;

.dialog-wrapper
  position: relative;
  height: 100%;
  transition: all 0.4s ease-out;
  &.col-7
    border-left: 1px solid $color-g4;
    border-right: 1px solid $color-g4;

  .header
    cursor: pointer;

  .debug
    font-family: Tahoma, Verdana, Segoe, sans-serif;
    margin-left: 3rem;

  .el-collapse-item__header
    cursor: pointer;

  .bottom
    position: absolute;
    left: 0;
    bottom: 1.5rem;

.bottom
  .send
    position: absolute;
    right: 1.5rem;
    top: 0.5rem;
    padding: 0.2rem;
    border-radius: 50%;
    border: 0;
    background: $color-c1;
    color: $color-white;
    height: 2rem;
    width: auto;
    cursor: pointer;
    padding: 0.2rem;
    .fa
      font-size: 1.3rem;

  input
    margin: 0;
    width: 100%;
    line-height: 2rem;
    padding: 0.5rem 1rem;
    border-radius: 5px;

/* message wrapper */
.dialog
  height: -webkit-calc(100% - 100px);
  height: calc(100% - 100px);
  overflow-y: scroll;
  padding: 1em 0;

.circle-wrapper
  height: 2rem;
  width: 2rem;
  border-radius: 50%;

.message-wrapper
  position: relative;
  width: 100%;
  margin: 0;
  padding: 1em;
  clear: both;
  .text-wrapper
    margin: 0 1em;
    padding: 0.5em 1em;
    max-width: 80%;
    font-weight: 500;
    position: relative;
    word-break: normal;
    background: $color-g5;
    border-radius: $border-radius-s;
    box-shadow: $box-shadow-s;
    .timestamp
      font-size: 0.7em;
      font-weight: 300;

  .circle-wrapper
    position: relative;
    height: 50px;
    width: 50px;
    border-radius: 50%;
    background: $color-g5;
    img
      position: absolute;
      width: 100%;
      height: 100%;
      left: 0;
      top: 0;

  a.more-forms
    color: $color-c1;
    cursor: pointer;
    font-size: 0.8em;

.message-wrapper.me
  text-align: right;
  .circle-wrapper,
  .text-wrapper
    float: right;

.message-wrapper.them
  text-align: left;
  .circle-wrapper,
  .text-wrapper
    float: left;

.debug-wrapper
  background-color: $color-g3;
  width: 90%;
  color: black;
  font-weight: 200;
  position: relative;
  margin: 0 auto;
  padding: 1em;
  border-radius: 2px;
  text-align: left;
  font-family: monaco, Consolas, "Lucida Console", monospace;
  pre
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: inherit;

/* sides */
.sidebar
  font-size: 0.7em;
  height: 100%;
  overflow: auto;
  text-align: left;
  .content
    overflow: scroll;
    height: calc(100vh - 200px);

  label
    display: block;
    text-transform: capitalize;

  input, textarea
    width: 100%;

.api-input-wrapper p
  padding-left: 1em;

.logging-wrapper
  .state
    border: 1px solid $color-g2;
    border-radius: 2em;
    padding: 0.5rem;
    line-height: 1rem;
    display: inline-block;
    margin: 0.5rem 0.3rem;

  .fa-icon
    color: $color-g3;
    font-weight: 70;

</style>
