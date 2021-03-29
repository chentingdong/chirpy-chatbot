<template>
  <div class="control-holder row"
    :class="name"
    @mousedown="disablePropergation($event)"
    @click="disablePropergation($event)"
    @dblclick="toggleExpand($event)">
    <label v-if="!isNodeTitle" class="col-3">{{label}}</label>
    <input
      :name="name"
      :value="value"
      @input="change($event)"
      :class="{'node-title' : isNodeTitle,'col-9': !isNodeTitle}"
      :placeholder="placeholder"
      :autocomplete="autocomplete"/>
  </div>
</template>

<script>
export default {
  props: ['name', 'emitter', 'ikey', 'getData', 'putData', 'label'],
  data () {
    return {
      value: '',
      readOnly: false,
      isNodeTitle: false,
      autocomplete: 'on',
      placeholder: ''
    }
  },
  methods: {
    change (e) {
      this.value = e.target.value
      this.update()
    },
    update () {
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
