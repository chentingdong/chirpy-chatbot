import Rete from 'rete'
import Radio from '../vue-control-components/Radio'

class RadioControl extends Rete.Control {
  constructor (name, emitter, label) {
    super(name)
    this.component = Radio
    this.props = { name, ikey: name, emitter, label }
  }

  setValue (val) {
    this.vueContext.value = val
  }
}

export default RadioControl
