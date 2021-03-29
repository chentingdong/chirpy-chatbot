<template>
  <div>
    <component :is="theme"></component>
  </div>
</template>

<script>
import Action from '@/pages/Demo/Action'
import Boa from '@/pages/Demo/Boa'
import Mcd from '@/pages/Demo/Mcd'
import Bose from '@/pages/Demo/Bose'
import { illusionistAPI } from '@/utils/rest-config'

export default {
  props: {
    agentId: String
  },
  components: {
    'default': Mcd,
    'action': Action,
    'boa': Boa,
    'mcd': Mcd,
    'bose': Bose
  },
  data: function () {
    return {
      theme: ''
    }
  },
  mounted: function () {
    this.getTheme()
  },
  methods: {
    getTheme: function () {
      const vm = this
      const path = '/api/agent/' + this.agentId
      illusionistAPI
        .get(path)
        .then((response) => {
          vm.theme = response.data.params.theme ? response.data.params.theme : 'default'
        })
    }
  }
}
</script>

<style lang="sass">
@import '@/assets/action.sass';

ul,
li
  padding: 0;
  list-style: none;

*:focus
  outline-color: transparent;
  outline-style: none;

*::-webkit-scrollbar
  width: 0px;
  background: transparent;

.click-effect

[v-cloak]
  display: none;

input
  padding: 0.2em 1em;

input:checked + .slider
  background-color: #48a5b8;

input:focus + .slider
  box-shadow: 1px 1px 1px 0px #999;

input:checked + .slider:before
  -webkit-transform: translateX(26px);
  -ms-transform: translateX(26px);
  transform: translateX(26px);

/* responsive design manual adjustments */
@include media-breakpoint-up(sm)
  .main
    height: calc(100vh - 100px);
  .container
    max-width: 1600px;
    padding: 1rem;

.tablet .demo .slide figure
    width: 60px;
    height: 60px;

@include media-breakpoint-up(md)
  html
    font-size: 1.2rem;
  .container
    max-width: 1960px;
    .dialog
      padding: 2rem 3rem;

@include media-breakpoint-up(lg)
  .container
    max-width: 2400px;
</style>
