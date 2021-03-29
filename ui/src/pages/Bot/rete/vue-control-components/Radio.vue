<template>
  <div class="control-holder row"
    @mousedown="disablePropergation($event)"
    @click="disablePropergation($event)"
    @dblclick="toggleExpand($event)">
    <label v-if="!isNodeTitle" class="col-3">{{label}}</label>
    <div v-for="(option, index) in options" v-bind:key="index" class="radio-button flex">
      <label :for="optionId(option)">
        <input type="radio"
          :id="optionId(option)"
          :name="Date.now()"
          :value="option"
          v-model="value"
          @input="change($event)"
        />
        <span>{{option}}</span>
      </label>
    </div>
  </div>
</template>

<script>
export default {
  props: ['name', 'emitter', 'ikey', 'getData', 'putData', 'label'],
  data () {
    return {
      value: '',
      options: ['update', 'append', 'reset'],
      selected_option: 'update',
      readOnly: false,
      isNodeTitle: false,
      autocomplete: 'on',
      placeholder: ''
    }
  },
  methods: {
    optionId (option) {
      return option + '-' + Date.now()
    },
    change (e) {
      this.value = e.target.value
      if (this.ikey) {
        this.putData(this.ikey, this.value)
      }
    },
    disablePropergation (e) {
      if (this.name !== 'name') {
        e.stopImmediatePropagation()
      }
    },
    toggleExpand (e) {
      e.stopImmediatePropagation()
      if (this.name === 'name') {
        var $node = e.target.parentElement.parentElement.parentElement
        if ($node.classList.value.includes('expand')) {
          $node.classList.remove('expand')
        } else {
          $node.classList.add('expand')
        }
      }
    }
  },
  mounted () {
    this.value = this.getData(this.ikey)
    if (this.name === 'start' || this.name === 'end') {
      this.autocomplete = 'off'
      this.readOnly = true
      this.isNodeTitle = true
      this.value = this.name
      this.putData('name', this.name)
      this.update()
    }
    if (this.name === 'name') {
      this.isNodeTitle = true
      this.autocomplete = 'off'
      this.placeholder = this.label
    }
  }
}
</script>
<style lang="scss" scoped>
.node .radio-button label {
  display: inline;
}
</style>
