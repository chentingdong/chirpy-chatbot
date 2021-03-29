<template>
  <div id="demo" class="demo bose container-fluid" xmlns:v-bind="http://www.w3.org/1999/xhtml">
    <header class="header bose">
      <img height="15" :src="boseLogo" />
      <span>Fetch, Service Hub assistant</span>
    </header>
    <div id="dialog" class="dialog">
      <div v-for="(message, index) in messageList" :key="'m-'+index">
        <div v-if="message.me" v-cloak class="well-lg me">
          <figure class="avatar-wrapper">
            <img class="animated bounceIn" :src="avatarUser" alt=""/>
          </figure>
          <div v-cloak class="text-wrapper animated fadeIn">
            <div class="message" v-html="message.message"></div>
          </div>
        </div>
        <div v-else-if="message.them" v-cloak class="well-lg them">
          <figure class="avatar-wrapper">
            <img class="animated bounceIn" :src="avatarAgent" alt=""/>
          </figure>
          <answer class="text-wrapper" :message="message" v-on:clickToMessage="clickToMessage"></answer>
        </div>
      </div>
      <div v-if="loading" class="well-lg them">
        <div v-cloak class="text-wrapper animated fadeIn">
          <figure class="avatar-wrapper">
            <img class="animated bounceIn" :src="avatarAgent" alt=""/>
          </figure>
          <loading></loading>
        </div>
      </div>
    </div>
    <footer>
      <input id="input" v-on:keyup.enter="sendMessage" v-model="inputMessage"
            :disabled="disableUserInput" :placeholder="inputPlaceholder"
            webkitSpeech="enabled" autofocus/>
      <div class="microphone float-right" v-on:click="sendMessage">
        <div class="img-rounded">
          <v-icon name="microphone"></v-icon>
        </div>
      </div>
      <div class="by-astound float-right"> Powered by Astound</div>
    </footer>
  </div>
</template>

<script>
'use strict'
import axios from 'axios'
import Answer from '@/pages/Answer'
import { illusionistAPI, apiPathSid } from '@/utils/rest-config'
const uuidv4 = require('uuid/v4')

export default {
  components: {
    'answer': Answer
  },
  data: function () {
    return {
      clientId: 'debugger',
      inputMessage: '',
      me: null,
      country: 'US',
      messenger: null,
      messageList: [],
      agentId: this.$route.params.agentId,
      reload: null,
      sessionId: '',
      stateHistory: [],
      loading: false,
      avatarUser: require('@/assets/user-avatar.png'),
      avatarAgent: require('@/assets/bose-avatar.png'),
      boseLogo: require('@/assets/bose_logo.png'),
      // Assume user will never type this special trigger message. Otherwise they just get welcome again.
      // Convension used in bot to match agent_driven answer node in index bot.
      checkAgentDrivenUtterance: 'check_agent_driven',
      userName: null
    }
  },
  computed: {
    speakMessage: function () {
      var msg = ''
      var message = this.messageList.slice(-2)[ 0 ]
      if (message && message.them && message.message && message.message.answer) {
        msg = message.message.answer
      }
      return msg
    },

    errorAnswer: function () {
      const answer = {
        'name': 'error',
        'pretext': 'Sorry, I didn\'t get that, please try again.'
      }
      return answer
    },

    disableUserInput: function () {
      var lastTemplate = ''
      if (this.messageList.length > 0) {
        lastTemplate = this.messageList[ this.messageList.length - 1 ][ 'message' ][ 'template' ]
      }
      var disableInput = false
      if (lastTemplate === 'text-buttons') {
        disableInput = true
      }
      return disableInput
    },

    inputPlaceholder: function () {
      return this.disableUserInput ? 'click a button' : ''
    }

  },

  mounted: function () {
    // document.getElementById('input').focus()
    this.checkAgentDriven()
  },

  methods: {
    checkAgentDriven () {
      const apiPath = '/api/1/check_agent_driven'
      const payload = {
        agent_id: this.$route.params.agentId
      }

      illusionistAPI
        .post(apiPath, payload)
        .then((response) => {
          const agentDriven = response.data.payloads.agent_driven
          if (agentDriven) {
            this.inputMessage = this.checkAgentDrivenUtterance
            this.sendMessage()
            this.inputMessage = ''
          }
        })
    },
    processMessage (data) {
      this.messageList.push({
        message: data,
        me: false,
        them: true,
        uuid: data.uuid,
        timestamp: new Date()
      })
    },

    checkInputMessage () {
      if (this.inputMessage === '') {
        return
      }
      this.sendMessage()
    },

    sendMessage () {
      if (!this.userName) {
        // this.fetchUserId()
      }
      const vm = this
      if (this.inputMessage !== null && vm.inputMessage !== vm.checkAgentDrivenUtterance) {
        vm.messageList.push({
          message: vm.inputMessage,
          me: true,
          them: false,
          timestamp: new Date()
        })
      }

      const apiPath = apiPathSid('/api/1/ask', vm.sessionId)
      const payload = vm.askPayload()
      vm.inputMessage = ''

      vm.loading = true
      if (this.sessionId === '') {
        this.sessionId = uuidv4()
      }

      illusionistAPI
        .post(apiPath, payload)
        .then((response) => {
          const states = response.data.payloads.state_history
          const answer = response.data.payloads.answer
          vm.sessionId = response.data.session_id
          if (vm.inputMessage !== vm.checkAgentDrivenUtterance) {
            vm.processMessage(answer)
          }
          vm.setStateHistory(states)
          console.log(answer)
        })
        .catch((e) => {
          console.log('ask api: ' + e)
          vm.processMessage(vm.errorAnswer)
        })
        .then(() => {
          vm.loading = false
        })
    },

    askPayload () {
      const payload = {
        agent_id: this.agentId,
        utterance: this.inputMessage,
        country: this.country,
        public_user_id: this.userName
      }
      return payload
    },

    isEmptyMessage () {
      var empty = this.inputMessage === null || this.inputMessage.match('/^ *$') !== null
      return empty
    },

    clickToMessage (message) {
      this.inputMessage = message
      this.sendMessage()
    },

    setStateHistory (states) {
      this.stateHistory = states
    },

    scrollBottom () {
      setTimeout(() => {
        var $dialogbox = document.getElementById('dialog')
        $dialogbo.scrollTop = $dialogbox.scrollHeight
      }, 1)
    },

    onTranscriptionEnd ({ lastSentence, transcription }) {
      console.debug(transcription)
      this.inputMessage = transcription[ transcription.length - 1 ]
      this.sendMessage()
    },
    fetchUserId () {
      const userProfileURL = 'Command/Authentication.EditUserInfo'
      axios.post(userProfileURL).then((response) => {
        const body = response.data
        const matchStringIndex = body.indexOf('setTitle')
        let usernameStartIndex = matchStringIndex + 10
        let userName = ''
        while (body[ usernameStartIndex ] !== '-') {
          userName = userName + body[ usernameStartIndex++ ]
        }
        userName = userName.trim()
        this.userName = userName
        console.log('username ' + userName)
      })
    }
  },
  watch: {
    'messageList': function () {
      this.scrollBottom()
    }
  }
}
</script>

<style lang="sass">
@import '@/assets/action.sass';

$bose-white: $color-white;
$bose-black: $color-black;
$border-radius-agent: 3rem;
$border-radius-user: 10px;
$color-user-light: #5dc2f5;

.demo.bose
  color: $bose-black;
  background-color: $bose-white;
  height: 100vh;
  font-family: Gotham Book, Arial;
  font-size: 21px;

  .header
    height: 26px;
    position: sticky;
    img
      height: 12px;
    span
      margin-left: 6px;
      font-size: initial;
  /* message wrapper */
  .dialog
    height: calc(100% - 90px);
    width: 100%;
    overflow-y: scroll;
    padding: 25px;

    .well-lg
      position: relative;
      min-width: 70%;
      margin: 12px 0;
      padding: 1rem;
      border-radius: $border-radius-user;
      line-height: 1em;
      overflow: visible;
      transition: height 0.5s ease;

      .text-wrapper
        font-weight: 500;
        word-break: normal;
        clear: both;
      .avatar-wrapper
        display: inline-block;
        position: absolute;
        top: -1.3em;
        height: 3.5rem;
        width: 3.5rem;
        border-radius: 50%;
        background-color: $bose-white;
        border: 2px solid $bose-black;
        overflow: hidden;

      &.me
        float: right;
        background: $bose-white;
        color: $bose-black;
        border: 1px solid $bose-black;
        border-radius: $border-radius-user;
        .avatar-wrapper
          right: -1.1rem;
          img
            height: 3.5rem;
            margin-left: -0.1rem;
            width: auto;
        .text-wrapper
          margin-right: 0.5em;
          text-align: right;

      &.them
        float: left;
        max-width: 100%;
        background: $bose-black;
        color: $bose-white;
        min-height: 2.5em;
        border-radius: $border-radius-agent;
        border-top-left-radius: 0;
        .avatar-wrapper
          left: -1.1rem;
          img
            margin-top: -0.1rem;
            height: 3.8rem;
            width: auto;
            padding: 0.5em;
            position: absolute;
        .text-wrapper
          margin-left: 1em;
          .btn-secondary
            background: $bose-white;
            color: $bose-black;

      ul.styled-list
        li
          list-style: disc;
          margin: 10px 0;
  footer
    input
      width: calc(100% - 5rem);
      padding: 0.2em 1em;
      margin: 0 1em 10px 0;
      border: 1px solid $bose-black;
    input::placeholder
      font-size: normal;
    .microphone
      .img-rounded
        position: relative;
        display: inline-block;
        border-radius: 50%;
        background: $bose-black;
        color: $bose-white;
        width: 3rem;
        height: 3rem;
        .fa-icon
          margin: 0.2rem 0 0 0.5rem;
          width: 2rem;
          height: 2rem;
    .by-astound
      font-size: 0.5em;
  .slide
    .inner
      background: $bose-white;
      color: $bose-black;
      box-shadow: none;
      border: none;
      padding: 5px 25px;
      border-radius: $border-radius-agent;
      h1
        color: #fff;
      a
        line-height: normal;
        font-weight: bold;
  .VueCarousel-pagination
    .VueCarousel-dot--active
      background-color: $color-g4 !important;
  .form-preview
    margin-top: 1em;
    border: 1px solid $bose-white;
  .VueCarousel-slide p
    line-height: normal;

</style>
