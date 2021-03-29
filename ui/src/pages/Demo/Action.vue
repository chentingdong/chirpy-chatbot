<template>
  <div id="demo" class="demo action container-fluid" xmlns:v-bind="http://www.w3.org/1999/xhtml">
    <header class="container-fluid text-center">
      <a class="" href="http://www.astound.ai">
        <img id="logo" src="@/assets/logo.png">
      </a>
    </header>
    <div id="dialog" class="dialog">
      <div v-for="(message, index) in messageList" :key="'m-'+index">
        <div v-if="message.me" v-cloak class="well-lg me">
          <figure class="avatar-wrapper">
            <img class="animated bounceIn" :src="avatarUser" alt=""/>
          </figure>
          <div v-cloak class="text-wrapper animated fadeIn">
            <div class="timestamp small">{{ message.timestamp | moment("MMMM Do, YYYY hh:mm:ss") }}</div>
            <div class="message" v-html="message.message"></div>
          </div>
        </div>
        <div v-else-if="message.them" v-cloak class="well-lg them">
          <figure class="avatar-wrapper">
            <img class="animated bounceIn" :src="avatarAgent" alt=""/>
          </figure>
          <div v-cloak class="text-wrapper animated fadeIn">
            <div class="timestamp small">{{ message.timestamp | moment("MMMM Do, YYYY hh:mm:ss") }}</div>
            <answer class="message" :message="message" v-on:sendMessage="sendMessageNoEmpty" v-on:clickToMessage="clickToMessage"></answer>
          </div>
        </div>
      </div>
      <div v-if="loading" class="well-lg them">
        <figure class="avatar-wrapper">
          <img class="animated bounceIn" :src="avatarAgent" alt=""/>
        </figure>
        <div v-cloak class="text-wrapper animated fadeIn">
          <div class="timestamp small">{{ currentTimestamp | moment("MMMM Do, YYYY hh:mm:ss") }}</div>
          <loading v-if="loading"></loading>
        </div>
      </div>
    </div>
    <footer>
      <div class="inner">
        <input id="input" class="input" v-on:keyup.enter="sendMessageNoEmpty" v-model="inputMessage" placeholder="" />
        <span class="send" v-on:click="sendMessageNoEmpty">
          <v-icon class="send" name="arrow-circle-right"></v-icon>
        </span>
        <!-- <voice @onTranscriptionEnd="onTranscriptionEnd" v-bind:speakMessage="speakMessage"></voice> -->
      </div>
    </footer>
  </div>
</template>

<script>
'use strict'
// import Voice from '@/components/Voice.vue'
import * as components from '@/components'
import Answer from '@/pages/Answer'
import { illusionistAPI, apiPathSid } from '@/utils/rest-config'
const uuidv4 = require('uuid/v4')

export default {
  components: Object.assign(
    components, {
      'answer': Answer
    }
  ),
  data: function () {
    return {
      clientId: 'debugger',
      company: '',
      country: 'Germany',
      dialog: null,
      firstName: 'Virtual Agent User',
      inputMessage: null,
      me: null,
      messenger: null,
      messageList: [],
      nevaAccessToken: '',
      agentId: this.$route.params.agentId,
      reload: null,
      instanceName: 'adidasaspenpreprod',
      virtualAgentUserId: 'virtual_agent',
      sessionId: '',
      stateHistory: [],
      token: null,
      url: null,
      loading: false,
      avatarUser: require('@/assets/user-2.jpeg'),
      avatarAgent: require('@/assets/favicon.png'),
      loadingImage: require('@/assets/loading-dots.gif')
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

    templates: function () {
      return [
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

    errorAnswer: function () {
      const answer = {
        'name': 'error',
        'pretext': 'Sorry, I didn\'t get that, please try again.'
      }
      return answer
    },

    currentTimestamp: function () {
      return new Date()
    }
  },

  mounted: function () {
    document.getElementById('input').focus()
    this.checkAgentDriven()
  },

  methods: {
    checkAgentDriven () {
      const apiPath = '/api/1/check_agent_driven'
      const payload = {
        agent_id: this.agentId
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
        uuid: data.uuid,
        timestamp: new Date()
      })
    },

    sendMessageNoEmpty () {
      if (this.inputMessage === '') {
        return
      }
      this.sendMessage()
    },

    sendMessage () {
      if (this.inputMessage !== null && this.inputMessage !== '') {
        this.messageList.push({
          message: this.inputMessage,
          me: true,
          them: false,
          timestamp: new Date()
        })
      }

      const payload = this.askPayload()
      this.inputMessage = ''
      const apiPath = apiPathSid('/api/1/ask', this.sessionId)

      this.loading = true
      illusionistAPI
        .post(apiPath, payload)
        .then((response) => {
          const states = response.data.payloads.state_history
          const answer = response.data.payloads.answer
          this.sessionId = response.data.session_id
          this.processMessage(answer)
          this.setStateHistory(states)
        })
        .catch((e) => {
          this.processMessage(this.errorAnswer)
        })
        .then(() => {
          this.loading = false
        })
    },

    askPayload () {
      const payload = {
        utterance: this.inputMessage,
        conversation_start: this.conversation_start,
        workflow: this.workflow,
        neva_access_token: this.nevaAccessToken,
        virtual_agent_user_id: this.virtualAgentUserId,
        client_id: this.clientId,
        agent_id: this.agentId,
        instance_name: this.instanceName,
        user_info: {
          first_name: this.firstName,
          country: this.$route.query.country ? this.$route.query.country : this.country,
          company: this.company
        },
        debug: true
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
<style lang="sass" scoped>
@import '@/assets/action.sass';
$color-body-bg: $color-g5;
$color-user: $color-g6;
$color-user-light: $color-g7;
$color-agent: $color-g5;
// $color-user: #7DE3B6;
// $color-user-light: #D2FDD2;
// $color-agent: #3e9998;

html
  font-size: 1rem;

@include media-breakpoint-up(sm)
  html
    font-size: 1.1rem;
  .container
    max-width: 1600px;
@include media-breakpoint-up(md)
  html
    font-size: 1.2rem;
  .container
    max-width: 1960px;
@include media-breakpoint-up(lg)
  html
    font-size: 1.5rem;
  .container
    max-width: 2400px;

$body-gradient: radial-gradient(farthest-corner at 50% 10%, rgba(255,255,255,0.7) 0, rgba(0,0,0, 0.3) 120%);
$hero-image: url('../../assets/hero-editor-2.png');

.demo.action
  width: 100%;
  height: 100vh;
  position: relative;
  background-image: $body-gradient, $hero-image;
  background-size: cover;

  header
    padding: 15px 0;
    img#logo
      height: 4rem;

  .dialog
    height: calc(100vh - 150px);
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
      .loading
        position: relative;
        float: left;
        left: 0;
        top: 0;
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
        top: 0.5rem;
        height: 2.5rem;
        width: 2.5rem;
        border-radius: 50%;
        background-color: $color-body;
        overflow: hidden;

      &.me
        float: right;
        background: $color-user;
        max-width: 90%;
        .avatar-wrapper
          right: 0.5rem;
          img
            height: 100%;
            width: auto;
            padding: 0;
        .text-wrapper
          margin-right: 3em;
          text-align: right;
          .message
            text-align: right;
      &.them
        float: left;
        background: $color-agent;
        max-width: 90%;
        min-height: 2.5em;
        .avatar-wrapper
          left: 0.5rem;
          background: none;
          img
            height: 2rem;
            padding: 0.2rem;
            width: auto;
        .text-wrapper
          margin-left: 3em;
          text-align: left;
          .btn-secondary
            border: none;

  footer
    margin: 10px 20px;
    position: relative;
    #input
      width: 100%;
      border-radius: $border-radius-s;
      background: $color-g5;
    .send
      height: 100%;
      width: 3em;
      padding: 0.3em 1em 0.3em 0.5em;
      position: absolute;
      right: 0;
      top: 0;
      cursor: pointer;
    .voice-wrapper
      position: absolute;
      right: 3em;
      top: 0.2em;

  /* debug hidden by default */
  .debug-wrapper
    display: none;
    background-color: #e9efef;
    width: 90%;
    color: black;
    font-weight: 200;
    font-size: 12px;
    position: relative;
    margin: 0 auto;
    padding: 10px 10px 10px 10px;
    border-radius: $border-radius-s;
    text-align: left;
    font-family: monaco, Consolas, "Lucida Console", monospace;
    pre
      white-space: pre-wrap;
      word-wrap: break-word;
      font-family: inherit;

</style>
