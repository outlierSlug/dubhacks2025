import * as api from './api'

export type Player = {
  id: number
  fname: string
  lname: string
  rating: number
  email: string
  phone: string
  bday: string
  gender: number
}

export async function signup(input: {
  username: string
  password: string
  id: number
  fname: string
  lname: string
  rating: number
  email: string
  phone: string
  bday: string
  gender: number
}): Promise<Player> {
  return api.signupUser(input)
}

export async function login(username: string, password: string): Promise<Player> {
  return api.loginUser(username, password)
}