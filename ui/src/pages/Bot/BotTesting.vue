<template>
  <div class="bot-testing container-fluid">
    <div class="row">Test result for current bot: {{passed}}</div>
    <div class="recording row">
      <button type="button" class="record btn btn-light" v-on:click="$emit('toggleRecordStop')">
        <v-icon name="stop"  v-if="recording" class="stop"></v-icon>
        <v-icon name="circle" v-else class="record"></v-icon>
      </button>
      <button type="button" class="play btn btn-light" v-on:click="$emit('togglePlayPause')">
        <v-icon name="pause" v-if="playing" class="pause"></v-icon>
        <v-icon name="play" v-else class="play"></v-icon>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    playing: false,
    recording: false,
    bot: {},
    botTestResult: {}
  },
  data: function () {
    return {
    }
  },
  computed: {
    passed: function () {
      var p = 'No recorded test.'
      if (this.botTestResult.test_passed === true) {
        p = 'Passed.'
      } else if (this.botTestResult.test_passed === false) {
        p = 'Failed.'
      }
      return p
    }
  },
  methods: {

  },
  watch: {
  }
}
</script>

<style lang="sass">
@import '@/assets/variables.scss';

.recording
  button
    font-size: 1em;
    width: 2.5em;
    line-height: 1.5em;
    margin-right: 0.5em;
  .play,
  .record
    color: $color-c4;
  .stop,
  .pause
    color: $color-c0;
</style>
