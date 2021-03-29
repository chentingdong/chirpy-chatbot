<template>
  <div class="bot-debugger">
    <div class="header">
      <!-- <div class="col-6">
        <label for="#debug-for-app">Debug for agent id: {{agentId}}</label>
        <v-select id="debug-for-agent" v-model="agentId" :options="bot.agents"></v-select>
      </div> -->
      <bot-testing :bot="bot"
                  :playing="playing"
                  :recording="recording"
                  :botTestResult="botTestResult"
                  v-on:toggleRecordStop="toggleRecordStop"
                  v-on:togglePlayPause="togglePlayPause"
                  ></bot-testing>
    </div>
    <div id="dialog-wrapper">
      <div class="dialog">
        <div v-for="(message, index) in messageList" :key="index">
          <div v-if="message.me" v-cloak class="message-wrapper me">
            <div v-cloak class="text-wrapper animated fadeIn">
              <div class="timestamp">{{ message.timestamp | moment("MMMM Do, YYYY hh:mm:ss") }}</div>
              <div v-html="message.message"></div>
            </div>
          </div>
          <div v-else-if="message.them" v-cloak class="message-wrapper them" v-bind:class="{debug: message.them==='debug'}">
            <div class="text-wrapper animated fadeIn">
              <div class="timestamp">{{ message.timestamp | moment("MMMM Do, YYYY hh:mm:ss") }}</div>
              <div v-html="message.message.pretext"></div>
              <div v-for="(component, index) in vm_components" :key="index">
                <component :is="component.name"
                  v-if="message.message.template===component.template"
                  v-bind:data_json="message.message.data"
                  v-on:clickToMessage="clickToMessage"></component>
                <component :is="component.name"
                  v-if="message.message.template_action===component.template"
                  v-bind:data_json="message.message.answer_action"
                  v-on:clickToMessage="clickToMessage"></component>
              </div>
              <div v-if="message.message.template_action==='plain-text'" v-html="message.message.answer_action"></div>
              <div v-if="message.message.template==='plain-text'" v-html="message.message.data"></div>
            </div>
          </div>
        </div>
        <loading v-if="loading"></loading>
      </div>
    </div>
    <div class="bottom">
      <input class="input" v-on:keyup.enter="sendMessage" v-model="inputMessage" placeholder="" />
      <span v-on:click="sendMessage">
        <v-icon class="send" name="arrow-circle-right" v-on:click="sendMessage"></v-icon>
      </span>
    </div>
  </div>
</template>

<script>
'use strict'
import axios from 'axios'
import * as components from '@/components'
import { illusionistAPI, apiPathSid } from '@/utils/rest-config'
import BotTesting from '@/pages/Bot/BotTesting'

const uuidv4 = require('uuid/v4')

export default {
  components: Object.assign(
    components, {
      'bot-testing': BotTesting
    }
  ),
  props: {
    bot: {},
    editor: {}
  },
  data: function () {
    return {
      action: 'text',
      clientId: 'bot debugger',
      content: null,
      company: 'Slack',
      country: 'United States of America',
      debugMode: true,
      dialog: null,
      firstName: 'Dan',
      group: '',
      input: null,
      inputMessage: null,
      me: null,
      messenger: null,
      messageList: [],
      reload: null,
      // instanceName: 'ven01702',
      sessionId: '',
      stateHistory: [],
      token: null,
      url: null,
      virtualAgentUserId: 'virtual_agent',
      recording: false,
      playing: false,
      loading: false,
      loadingMessage: '',
      botTestResult: {}
    }
  },
  computed: {
    vm_components: function () {
      return [
        { 'name': 'AgentHeader', 'template': 'agent-header' },
        { 'name': 'ImageButtons', 'template': 'image-buttons' },
        { 'name': 'ImageSlides', 'template': 'image-slides' },
        { 'name': 'LinkButtons', 'template': 'link-buttons' },
        { 'name': 'PizzaReceipt', 'template': 'pizza-receipt' },
        { 'name': 'SimpleTable', 'template': 'simple-table' },
        { 'name': 'DataSlides', 'template': 'data-slides' },
        { 'name': 'TextButtons', 'template': 'text-buttons' },
        { 'name': 'GoogleSearchResult', 'template': 'google-search-result' },
        { 'name': 'CarouselLinks', 'template': 'carousel-links' }
      ]
    },
    speakMessage: function () {
      var msg = ''
      var message = this.messageList.slice(-2)[ 0 ]
      if (message && message.them && message.message && message.message.pretext) {
        msg = message.message.pretext
      }
      return msg
    },
    askUrl: function () {
      const vm = this
      if (vm.sessionId === '') {
        vm.sessionId = uuidv4()
      }
      const askUrl = '/api/1/ask_bot/?session_id=' + vm.sessionId
      return askUrl
    },
    askPayload: function () {
      const vm = this
      const payLoad = {
        utterance: vm.inputMessage,
        virtual_agent_user_id: vm.virtualAgentUserId,
        client_id: vm.clientId,
        // agent_id: vm.agentId,
        user_info: {
          first_name: vm.firstName,
          country: vm.country,
          company: vm.company,
          group: vm.group
        },
        debug: true,
        bot_name: vm.bot.name
      }
      console.log(`ask payload: ${JSON.stringify(payLoad)}`)
      return payLoad
    }
    // agentId: function () {
    //   return this.bot.agents[ 0 ]
    // }
  },
  mounted: function () {
    const vm = this
    vm.$dialogBox = document.getElementById('dialog-wrapper')
    window.onbeforeunload = function () {
      vm.clearSession()
    }
  },
  watch: {
    messageList: function () {
      this.scrollBottom()
    },
    bot: function () {
      this.getBotTestResult()
    }
  },
  methods: {
    processAgentMessage (data) {
      this.messageList.push({
        message: data,
        me: false,
        them: true,
        timestamp: new Date()
      })
    },

    processUserMessage () {
      const vm = this
      vm.messageList.push({
        message: vm.inputMessage,
        me: true,
        them: false,
        timestamp: new Date()
      })
      vm.inputMessage = ''
    },

    async sendMessage () {
      var vm = this
      if (vm.inputMessage === null || vm.inputMessage.match('/^ *$') !== null) {
        return
      }

      var askPayload = vm.askPayload
      vm.processUserMessage()

      vm.loading = true
      vm.loadingMessage = 'Agent typing ...'
      const apiPath = apiPathSid('/api/1/ask_bot/' + vm.bot.id, vm.sessionId)
      await illusionistAPI
        .post(apiPath, askPayload)
        .then((response) => {
          const states = response.data.payloads.state_history
          const answer = response.data.payloads.answer
          vm.sessionId = response.data.session_id
          vm.processAgentMessage(answer)
          vm.setStateHistory(states)
          // vm.updateCurrentBot(response.data.payloads)
          vm.highlightCurrentNode(answer)
        })
        .catch((e) => {
          console.error(e)
          const answer = { 'pretext': vm.bot.params.answer_error }
          vm.processAgentMessage(answer)
        })
        .then(() => {
          vm.loading = false
          vm.loadingMessage = ''
        })
      return true
    },

    clickToMessage (message) {
      this.inputMessage = message
      this.sendMessage()
    },

    setStateHistory (states) {
      this.stateHistory = states
    },

    highlightCurrentNode (answer) {
      var vm = this
      Object.keys(vm.editor.nodes).forEach(function (key) {
        vm.editor.nodes[ key ].vueContext.$el.classList.remove('highlight')
      })

      var node_name = answer.name
      if (node_name !== undefined) {
        const highlight_node = vm.editor.nodes.find(n => n.data.name === node_name)
        highlight_node.vueContext.$el.classList.add('highlight')
      }
    },

    scrollBottom () {
      var vm = this
      setTimeout(() => {
        vm.$dialogBox.scrollTop = vm.$dialogBox.scrollHeight
      }, 10)
    },

    clearSession () {
      const endUrl = '/end?session_id=' + this.sessionId
      if (this.sessionId) {
        this.$http.get(endUrl + this.sessionId).then(data => {
          return 'Are you sure?'
        }).catch(e => {
          console.error(e)
        })
      }
    },

    onTranscriptionEnd ({ lastSentence, transcription }) {
      console.debug(transcription)
      this.inputMessage = transcription[ transcription.length - 1 ]
      this.sendMessage()
    },

    /* bot testing */
    toggleRecordStop () {
      const vm = this
      if (this.playing) {
        return
      }

      vm.recording = !vm.recording

      if (vm.recording) {
        vm.newSession()
        vm.messageList = []
        const intent = vm.bot.intent.positives[ 0 ]
        if (intent) {
          vm.inputMessage = intent
          vm.sendMessage()
        }
      } else {
        vm.saveBotTestingSet(vm.messageList)
      }
    },

    newSession () {
      this.sessionId = uuidv4()
    },

    togglePlayPause () {
      const vm = this
      if (vm.recording) {
        return
      }

      vm.playing = !vm.playing

      if (vm.playing) {
        vm.newSession()
        vm.playBotTestingSet()
      }
    },

    saveBotTestingSet (testSet) {
      const vm = this

      if (vm.sessionId === '') {
        vm.sessionId = uuidv4()
      }

      const payload = {
        'id': vm.bot.id,
        'name': vm.bot.name,
        'test_set': testSet,
        'test_passed': true
      }

      const prevTestSet = vm.botTestResult.test_set
      console.log(prevTestSet)
      if (!prevTestSet) {
        vm.createBotTestingSet(payload)
      } else {
        vm.updateBotTestingSet(payload)
      }
    },

    createBotTestingSet (payload) {
      const vm = this

      const message = {
        title: 'Create',
        body: `Create test data for bot ${vm.bot.id}?`
      }

      const options = {
        okText: 'Yes, Create',
        cancelText: 'No, do not create'
      }

      vm.loading = true
      const botTestingUrl = '/api/test_bot'
      vm.$dialog
        .confirm(message, options)
        .then(() => {
          illusionistAPI
            .post(botTestingUrl, payload)
            .then((dialog) => {
              vm.$dialog.alert(`Successfully created test data set for ${vm.bot.id}`)
            })
            .catch((e) => {
              vm.$dialog.alert(`Failed creating test data set, error: ${e}`)
            })
        })
        .then(() => {
          vm.loading = false
        })
    },

    updateBotTestingSet (payload) {
      const vm = this

      const message = {
        title: 'Update',
        body: `Update test data for bot ${vm.bot.id}?`
      }

      const options = {
        okText: 'Yes, Update',
        cancelText: 'No, do not update'
      }

      const apiPath = '/api/test_bot/' + vm.bot.id
      vm.loading = true
      vm.$dialog
        .confirm(message, options)
        .then(() => {
          illusionistAPI
            .put(apiPath, payload)
            .then((dialog) => {
              vm.$dialog.alert(`Successfully updated bot testing data set for ${vm.bot.id}`)
            })
            .catch((e) => {
              console.warn(`Failed updating bot testing data set, error: ${e}`)
            })
        })
        .then(() => {
          vm.loading = false
        })
    },

    async playBotTestingSet () {
      const vm = this
      vm.clearSession()

      vm.messageList = []

      var compareMessage = function (them, themRecorded) {
        const m1 = them.message
        const m2 = themRecorded.message
        const m1j = JSON.stringify(m1, Object.keys(m1).sort())
        const m2j = JSON.stringify(m2, Object.keys(m2).sort())

        return m1j === m2j
      }

      const testSet = vm.botTestResult.test_set
      while (testSet.length > 0) {
        const me = testSet.shift()
        const themRecorded = testSet.shift()
        vm.inputMessage = me.message
        await vm.sendMessage()

        const them = vm.messageList.slice(-1)[ 0 ]
        const compareResult = compareMessage(them, themRecorded)
        if (!compareResult) {
          const debugMessage = themRecorded
          debugMessage.them = 'debug'
          vm.messageList.push(debugMessage)
          vm.clearSession()
          break
        }
      }
      vm.playing = false
    },
    getBotTestResult () {
      const vm = this
      const apiPath = '/api/test_bot/' + vm.bot.id
      illusionistAPI
        .get(apiPath)
        .then((response) => {
          vm.botTestResult = response.data
        })
        .catch((e) => {
          console.warn('No test result for this bot. ' + e)
        })
    }
  }
}
</script>

<style lang="sass">
@import '@/assets/variables.scss';

.bot-debugger
  padding: 10px 0;
  position: relative;
  box-sizing: border-box;
  height: calc(100vh - 100px);

#dialog-wrapper
  transition: all 0.4s ease-out;
  height: calc(100vh - 220px);
  width: 100%;
  overflow: auto;
  transition: scrollTop 300ms cubic-bezier(0.1, 0.7, 1, 0.1);
  border-top: 1px solid $color-body;
  margin-top: 10px;
  .dialog
    .loading
      position: relative;
      left: 0;
      img
        height: 41px;
        width: auto;

  .message-wrapper
    &.me
      text-align: right;
      .circle-wrapper
        float: right;

    &.them
      text-align: left;
      .circle-wrapper
        float: left;
      // &.debug
      //   color: $color-c0;

    .timestamp
      font-size: 0.8em;

.bottom
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  .input
    margin: 0;
    padding: 0.3em 2.5em 0.3em 0.5em;
    width: 100%;
    border: 1px solid $color-g4;

  .send
    height: 100%;
    width: 3em;
    padding: 0.3em 0.5em;
    position: absolute;
    right: 0;
    top: 0;
    cursor: pointer;

.timestamp
  font-weight: 700;

</style>
