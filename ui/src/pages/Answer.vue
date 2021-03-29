<template>
  <div class="answer animated fadeIn">
    <div v-html="message.message.pretext"></div>
    <div v-for="(template, index) in templates" :key="'t1-'+index">
      <component :is="template.name"
                v-if="template.template===message.message.template_action"
                v-bind:data_json="message.message.answer_action"
                v-on:clickToMessage="clickToMessage"></component>
    </div>
    <div v-if="message.message.pretext2" v-html="message.message.pretext2"></div>
    <div v-for="(template, index) in templates" :key="'t2-'+index">
      <component :is="template.name"
        v-if="template.template===message.message.template"
        v-bind:data_json="message.message.data"
        v-on:clickToMessage="clickToMessage"
      ></component>
    </div>
    <div v-if="message.message.template_action==='plain-text'" v-html="message.message.answer_action"></div>
    <div v-if="message.message.template==='plain-text'" v-html="message.message.data"></div>
  </div>
</template>

<script>

import * as components from '@/components'

export default {
  components: Object.assign(
    components, {
    }
  ),
  props: {
    message: Object
  },
  data: function () {
    return {
      loading: false
    }
  },
  computed: {
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
        { 'name': 'CarouselLinks', 'template': 'carousel-links' },
        { 'name': 'FormPreview', 'template': 'form-preview' }
      ]
    }
  },
  methods: {
    clickToMessage (message) {
      this.$emit('clickToMessage', message)
    }
  }
}
</script>
<style lang='sass'>
@import '@/assets/variables.scss';
.answer
  .text-wrapper
    text-align: left;
    font-weight: 500;
    color: $color-body;
    word-break: normal;
    clear: both;
    min-height: 3em;

  .avatar-wrapper
    display: inline-block;
    position: absolute;
    top: 0.5em;
    height: 2.5rem;
    width: 2.5rem;
    background-color: transparent;
    overflow: hidden;
    img
      height: 100%;
      width: auto;

  .loading
    z-index: 10;
    background: transparent;
    position: relative;
    float: left;
    left: auto;
    img
      height: 41px;
      width: auto;
      position: relative;
      float: left;

</style>
