<template>
  <div id="demo" class="demo boa container-fluid" xmlns:v-bind="http://www.w3.org/1999/xhtml">
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
        <figure class="avatar-wrapper">
          <img class="animated bounceIn" :src="avatarAgent" alt=""/>
        </figure>
          <loading></loading>
      </div>
    </div>
    <footer class="row">
      <input id="input" v-on:keyup.enter="sendMessageNoEmpty" v-model="inputMessage" placeholder="" webkitSpeech="enabled" />
      <div class="microphone" v-on:click="sendMessageNoEmpty">
        <div class="img-rounded">
          <v-icon name="microphone"></v-icon>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
'use strict'
import Answer from '@/pages/Answer'
import { illusionistAPI, apiPathSid } from '@/utils/rest-config'

export default {
  components: {
    'answer': Answer
  },
  data: function () {
    return {
      clientId: 'debugger',
      company: '',
      country: '',
      firstName: 'Virtual Agent User',
      inputMessage: '',
      me: null,
      messenger: null,
      messageList: [],
      nevaAccessToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTc0Nywib3JnX2lkIjoxLCJvcmciOnsiaWQiOjF9LCJpYXQiOjE0OTQwODE1NTF9.xkERCo-5gFCY8xlgIbm7gqQav7HpclZ9MtTUfZCcrkA',
      agentId: this.$route.params.agentId,
      reload: null,
      instanceName: 'ven01701',
      virtualAgentUserId: 'virtual_agent',
      sessionId: '',
      stateHistory: [],
      token: null,
      url: null,
      loading: false,
      avatarUser: require('@/assets/bashayir.png'),
      avatarAgent: require('@/assets/favicon.png')
    }
  },
  computed: {
    errorAnswer: function () {
      const answer = {
        'name': 'error',
        'pretext': 'Sorry, I didn\'t get that, please try again.'
      }
      return answer
    }
  },

  mounted: function () {
    document.getElementById('input').focus()
    this.checkAgentDriven()
  },

  methods: {
    checkAgentDriven () {
      const apiPath = apiPathSid('/api/1/check_agent_driven', this.sessionId)
      const payload = {
        agent_id: this.$route.params.agentId
      }

      illusionistAPI
        .post(apiPath, payload)
        .then((response) => {
          const agentDriven = response.data.payloads.agent_driven
          if (agentDriven) {
            this.sendMessage()
          }
        })
    },

    processMessage (data) {
      this.messageList.push({
        message: data,
        me: false,
        them: true,
        uuid: data.uuid
      })
    },

    sendMessageNoEmpty () {
      if (this.inputMessage === '') {
        return
      }
      this.sendMessage()
    },

    sendMessage () {
      const vm = this
      if (this.inputMessage !== null && vm.inputMessage !== '') {
        vm.messageList.push({
          message: vm.inputMessage,
          me: true,
          them: false
        })
      }

      const apiPath = apiPathSid('/api/1/ask', vm.sessionId)
      const payload = vm.askPayload()
      vm.inputMessage = ''

      vm.loading = true

      illusionistAPI
        .post(apiPath, payload)
        .then((response) => {
          const states = response.data.payloads.state_history
          const answer = response.data.payloads.answer
          vm.sessionId = response.data.session_id
          vm.processMessage(answer)
          vm.setStateHistory(states)
          console.log(answer)
          vm.inputMessage = ''
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
        workflow: this.workflow,
        neva_access_token: this.nevaAccessToken,
        virtual_agent_user_id: this.virtualAgentUserId,
        client_id: this.clientId,
        instance_name: this.instanceName,
        user_info: {
          first_name: this.firstName,
          country: this.$route.query.country ? this.$route.query.country : this.country,
          company: this.company
        },
        debug: true
      }
      console.log(payload)
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
        $dialogbox.scrollTop = $dialogbox.scrollHeight
      }, 1)
    },

    onTranscriptionEnd ({ lastSentence, transcription }) {
      console.debug(transcription)
      this.inputMessage = transcription[ transcription.length - 1 ]
      this.sendMessage()
    }
  },
  watch: {
    messageList () {
      this.scrollBottom()
    }
  }
}
</script>

<style lang="sass">
@import '@/assets/action.sass';

$color-body-bg: #1a2238;
$color-user: #0c6ba6;
$color-agent: #164070;
$color-user-light: #5dc2f5;
$color-body: #ffffff;

.demo.boa
  color: $color-body;
  background-color: $color-body-bg;
  background-size: cover;
  height: 100vh;

  .main
    height: 100%;
    position: relative;
    overflow: visible;

  .debug
    font-family: Tahoma, Verdana, Segoe, sans-serif;
    font-size: 0.7em;
    margin-left: 30px;

  /* message wrapper */
  .dialog
    height: calc(100% - 50px);
    width: 100%;
    overflow-y: scroll;
    padding: 25px;

    .well-lg
      position: relative;
      min-width: 70%;
      border-radius: $border-radius-m;
      margin: 5px 0;
      padding: 1em 2em;
      overflow: visible;

      .text-wrapper
        font-weight: 500;
        font-face: Helvetica;
        color: $color-body;
        word-break: normal;
        clear: both;
        min-height: 2em;

      .avatar-wrapper
        display: inline-block;
        position: absolute;
        top: -1.3em;
        height: 2.5rem;
        width: 2.5rem;
        border-radius: 50%;
        background-color: $color-body;
        overflow: hidden;

      &.me
        float: right;
        background: $color-user;
        .avatar-wrapper
          right: -1.1em;
          border: 0.2rem solid $color-user-light;
          img
            height: 2.2rem;
            margin-left: 0.1rem;
            width: auto;
        .text-wrapper
          margin-right: 0.5em;
          text-align: right;
      &.them
        float: left;
        background: $color-agent;
        min-height: 2.5em;
        max-width: 90%;
        .avatar-wrapper
          left: -1.1em;
          img
            width: 2.6rem;
        .text-wrapper
          margin-left: 1em;
          .btn-secondary
            background: $color-user;
            border: none;
  footer
    text-align: center;
    input
      width: calc(100% - 5rem);
      padding: 0.2em 1em;
      margin: 0 1rem;
      background: $color-user;
    .microphone
      .img-rounded
        position: relative;
        display: inline-block;
        border-radius: 50%;
        background: red;
        width: 2.2rem;
        height: 2.2rem;
        .fa-icon
          margin: 0.25rem;
          width: 1.5rem;
          height: 1.5rem;

  /* overriding component themes */
  .slide
    max-width: 500px;
    .inner
      border-color: $color-user;
      border-left-color: $color-user-light;
      box-shadow: 1px 1px 2px 0px $color-user;
      background: none;
      border-color: $color-user;
      border-left: 5px solid $color-user-light;
      box-shadow: 1px 2px 2px 0px $color-user;
      color: #fff;
      line-height: 1.2em;
      a
        color: $color-body;
        font-weight: 700;
        font-size: 1.2em;
      .text h1
        color: $color-body;
        font-size: 1.5em;
</style>
