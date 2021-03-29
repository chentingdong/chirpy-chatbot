<template>
  <div class="voice-wrapper">
    <span>{{ runtimeTranscription }}</span>
    <span v-bind:class="{ hidden: !micSwitch }"  v-on:click="toggleMic">
      <v-icon name="microphone" />
    </span>
    <span v-bind:class="{ hidden: micSwitch }"  v-on:click="toggleMic">
      <v-icon name="microphone-slash" />
    </span>
    <span v-bind:class="{ hidden: !speakerSwitch }" v-on:click="toggleSpeaker">
      <v-icon name="volume-up" />
    </span>
    <span v-bind:class="{ hidden: speakerSwitch }" v-on:click="toggleSpeaker">
      <v-icon name="volume-off" />
    </span>
</div>
</template>
<script>
export default {
  name: 'voice',
  props: {
    lang: {
      type: String,
      default: 'en-US'
    },
    speakMessage: {
      type: String,
      default: ' '
    }
  },
  data: () => ({
    micSwitch: false,
    speakerSwitch: false,
    recognition: {},
    synthesis: {},
    runtimeTranscription: '',
    transcription: []
  }),
  methods: {
    checkBrowser () {
      var supportMic = false

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (SpeechRecognition) {
        supportMic = true
        this.recognition = new SpeechRecognition()
      } else {
        console.error('Speech Recognition does not exist on this browser. Use Chrome or Firefox')
      }

      var supportSpeaker = false
      if ('speechSynthesis' in window) {
        supportSpeaker = true
      }
      return supportMic && supportSpeaker
    },
    initMic () {
      this.recognition.lang = this.lang
      this.recognition.interimResults = this.interimResults

      this.recognition.addEventListener('result', event => {
        const text = Array.from(event.results)
          .map(result => result[ 0 ])
          .map(result => result.transcript)
          .join('')
        this.runtimeTranscription = text
      })

      this.recognition.addEventListener('end', () => {
        if (this.runtimeTranscription !== '') {
          this.transcription.push(this.runtimeTranscription)
          this.$emit('onTranscriptionEnd', {
            transcription: this.transcription,
            lastSentence: this.runtimeTranscription
          })
        }
        this.runtimeTranscription = ''
      })
    },
    speak () {
      const self = this

      if (self.speakerSwitch === false) {
        return
      }

      self.micSwitch = false

      var msg = new SpeechSynthesisUtterance()
      msg.text = this.speakMessage
      window.speechSynthesis.speak(msg)

      msg.onend = function (event) {
        var speakTime = event.elapsedTime / 1000
        console.debug('synthesis took ' + speakTime.toFixed(3) + ' seconds')
        self.micSwitch = true
      }
    },
    toggleSpeaker () {
      if (this.speakerSwitch) {
        this.speakerSwitch = false
      } else {
        this.speakerSwitch = true
      }
    },
    toggleMic () {
      if (this.micSwitch) {
        this.micSwitch = false
      } else {
        this.micSwitch = true
      }
    }
  },
  mounted () {
    if (this.checkBrowser()) {
      this.initMic()
    }
  },
  watch: {
    speakMessage: function (val) {
      this.speak(val)
    },
    micSwitch: function (val) {
      if (val === 'on') {
        this.recognition.start()
        console.debug('Mic on.')
      } else {
        this.recognition.abort()
        console.debug('Mic off.')
      }
    }
  } }
</script>
<style>
.hidden {
  display: none;
}
</style>
