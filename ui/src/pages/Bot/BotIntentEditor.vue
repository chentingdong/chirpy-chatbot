<template>
  <div class="intent-editor">
    <div class="field">
      <h3>name: </h3>
      <input class="col-12" type="text" v-model="bot.name" />
    </div>
    <div class="field">
      <h3>description: </h3>
      <textarea class="col-12" v-model="bot.description" />
    </div>
    <!-- <div class="field">
      <h3>engine: </h3>
      <input class="col-12" type="text" v-model="bot.params.engine" />
    </div> -->
    <!-- <div class="field">
      <h3>match method: </h3>
      <v-select class="col-12" type="text" v-model="bot.params.match_method" :options="match_methods"/>
    </div> -->
    <div class="field">
      <h3>domains:</h3>
      <v-select v-model="bot.intent.domains" :options="domains"></v-select>
    </div>
    <div class="field">
      <h3>tags:</h3>
      <tags-input v-model="bot.intent.tags"></tags-input>
    </div>
    <div class="field">
      <h3 class="">
        <span>Intention Prototypes:</span>
        <span class="col-1 clickable" v-on:click="addIntentCase('positive')">
          <v-icon name="plus-circle"></v-icon>
        </span>
      </h3>
      <ul class="intents">
        <li class="row" v-for="(intent, index) in bot.intent.positives" v-bind:key="index">
          <input type="text" class="col-10" v-bind:value="intent" v-on:change="bot.intent.positives[index] = $event.target.value "/>
          <span class="col-1 clickable" v-on:click="deleteIntentCase('positive', index)">
            <v-icon name="times-circle"></v-icon>
          </span>
        </li>
      </ul>
    </div>
    <!-- <div class="field">
      <h3 class="row">
        <span>negative cases </span>
        <span class="col-1 clickable" v-on:click="addIntentCase('negative')">
          <v-icon name="plus-circle"></v-icon>
        </span>
      </h3>
      <ul class="intents">
        <li class="row" v-for="(intent, index) in bot.intent.negatives" v-bind:key="index">
          <input type="text" class="col-11" v-bind:value="intent" v-on:change="bot.intent.negatives[index] = $event.target.value "/>
          <span class="col-1 clickable" v-on:click="deleteIntentCase('negative', index)">
            <v-icon name="times-circle"></v-icon>
          </span>
        </li>
      </ul>
    </div> -->
    <!-- <div class="field">
      <h3>answer for not related</h3>
      <textarea type="text" class="col-12" v-model="bot.params.answer_not_related" ></textarea>
    </div>
    <div class="field">
      <h3>answer for error case</h3>
      <textarea type="text" class="col-12" v-model="bot.params.answer_error" ></textarea>
    </div> -->
    <div class="field">
      <input id="enable" type="checkbox" v-model="bot.enabled" /> &nbsp;
      <label for="enable">Enabled: {{bot.enabled}}</label>&nbsp;&nbsp;&nbsp;
      <input id="searchable" type="checkbox" v-model="bot.searchable" />&nbsp;
      <label for="searchable">Searchable: {{bot.searchable}}</label>
    </div>
    <div class="field">
      <div class="row">
        <span class="col-4">created on: </span>
        <span class="col-8">{{bot.created_on}}</span>
      </div>
      <div class="row">
        <span class="col-4">changed on: </span>
        <span class="col-8">{{bot.changed_on}}</span>
      </div>
    </div>
    <div class="field">
      <h3>agents</h3>
      <v-select v-model="bot.agents" :options="allAgents" multiple></v-select>
    </div>
  </div>
</template>

<script>
// import InputTag from 'vue-input-tag'
import VoerroTagsInput from '@voerro/vue-tagsinput'
import { agentMixins } from '@/utils/vue-mixin'

export default {
  name: 'BotIntentEditor',
  components: {
    'tags-input': VoerroTagsInput
  },
  props: {
    bot: {}
  },
  data () {
    return {
      match_methods: [ 'luke', 'spacy' ],
      domains: [ '', 'IT', 'HR', 'FINANCE' ],
      allTags: [],
      allAgents: []
    }
  },
  mounted: function () {
    this.fetchAllAgents()
  },
  mixins: [ agentMixins ],
  methods: {
    selectEngine (event) {
      this.bot.engine = this.engines[ event.target.selectedIndex ]
      console.log(this.bot.engine)
    },
    addIntentCase (caseType) {
      if (caseType === 'positive') {
        if (this.bot.intent.positives === undefined) {
          this.bot.intent.positives = [ '' ]
        } else {
          this.bot.intent.positives.push('')
        }
      } else if (caseType === 'negative') {
        if (this.bot.intent.negatives === undefined) {
          this.bot.intent.negatives = [ '' ]
        } else {
          this.bot.intent.negatives.push('')
        }
      } else {
        console.log('Adding new intent failed.')
      }
    },
    deleteIntentCase (caseType, index) {
      if (caseType === 'positive') {
        this.bot.intent.positives.splice(index, 1)
      } else if (caseType === 'negative') {
        this.bot.intent.negatives.splice(index, 1)
      } else {
        console.log('Adding new intent failed.')
      }
    }
  }
}
</script>

<style lang="sass" scoped>
@import "@/assets/variables.scss";

.intent-editor
  background-repeat: no-repeat;
  background-size: cover;
  height: 100%;
  .field
    margin: 15px 0;
  input, textarea
    border: 1px solid $color-g3;
    border-radius: $border-radius;
  ul.intents
    padding-left: 0;
    li
      margin: 10px 0;
  .clickable
    cursor: pointer;
  h3
    font-size: 0.8em;
    font-weight: 300;
  .nav-tabs
    font-weight: 700;
    .nav-link
      background: transparent;
</style>
