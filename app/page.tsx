// @ts-nocheck
"use client"

import { useEffect, useRef, useState } from "react"

// Game constants
const SCREEN_WIDTH = 1200
const SCREEN_HEIGHT = 800
const GRAVITY = 0.8
const FRICTION = 0.85
const GROUND_Y = SCREEN_HEIGHT - 100
const PLATFORM_HEIGHT = 20
const MAX_HEALTH = 100
const MAX_FPS = 60

// Retro color palette
const COLORS = {
  primary: "#00ff41",
  secondary: "#ff0080",
  accent: "#00ffff",
  success: "#00ff00",
  warning: "#ffff00",
  danger: "#ff0040",
  dark: "#000000",
  darker: "#0a0a0a",
  light: "#ffffff",
  neon: {
    green: "#00ff41",
    pink: "#ff0080",
    cyan: "#00ffff",
    yellow: "#ffff00",
    purple: "#8000ff",
    orange: "#ff8000",
  },
  retro: {
    bg: "#0a0a0a",
    panel: "#1a1a1a",
    border: "#333333",
    text: "#00ff41",
    accent: "#ff0080",
  },
}

// Default keybinds
const DEFAULT_KEYBINDS = {
  up: "KeyW",
  left: "KeyA",
  down: "KeyS",
  right: "KeyD",
  attack: "KeyF",
  special: "KeyG",
  emote1: "Digit1",
  emote2: "Digit2",
  emote3: "Digit3",
}

// Game modes
const GAME_MODES = {
  classic: {
    name: "CLASSIC",
    description: "Traditional 1v1 fighting",
    coins: 50,
    icon: "⚔",
  },
  survival: {
    name: "SURVIVAL",
    description: "Fight waves of enemies",
    coins: 75,
    icon: "🛡",
  },
  timeAttack: {
    name: "TIME ATTACK",
    description: "Defeat opponent quickly",
    coins: 60,
    icon: "⏱",
  },
  tournament: {
    name: "TOURNAMENT",
    description: "Bracket-style competition",
    coins: 100,
    icon: "🏆",
  },
  practice: {
    name: "PRACTICE",
    description: "Train your skills",
    coins: 10,
    icon: "🎯",
  },
}

// Enhanced character definitions with unlock requirements
const CHARACTERS = {
  // Free characters
  blaze: {
    name: "BLAZE",
    color: "#ff0040",
    secondaryColor: "#ff4080",
    width: 50,
    height: 80,
    speed: 8,
    jump_power: 18,
    attack_power: 10,
    special_power: 25,
    description: "Balanced fighter with fiery combat skills",
    rarity: "common",
    unlocked: true,
    cost: 0,
    abilities: ["Fire Nova", "Flame Dash", "Burning Strike"],
  },
  verdant: {
    name: "VERDANT",
    color: "#00ff00",
    secondaryColor: "#40ff40",
    width: 50,
    height: 85,
    speed: 6,
    jump_power: 16,
    attack_power: 12,
    special_power: 30,
    description: "Nature warrior with powerful strikes",
    rarity: "common",
    unlocked: true,
    cost: 0,
    abilities: ["Vine Whip", "Root Trap", "Nature's Wrath"],
  },
  nimbus: {
    name: "NIMBUS",
    color: "#00ffff",
    secondaryColor: "#40ffff",
    width: 45,
    height: 45,
    speed: 10,
    jump_power: 22,
    attack_power: 8,
    special_power: 20,
    description: "Agile cloud spirit with high mobility",
    rarity: "common",
    unlocked: true,
    cost: 0,
    abilities: ["Cloud Dash", "Lightning Strike", "Wind Burst"],
  },
  // Shop characters
  shadow: {
    name: "SHADOW",
    color: "#8000ff",
    secondaryColor: "#a040ff",
    width: 48,
    height: 82,
    speed: 9,
    jump_power: 20,
    attack_power: 11,
    special_power: 28,
    description: "Master of darkness and stealth",
    rarity: "rare",
    unlocked: false,
    cost: 500,
    abilities: ["Shadow Clone", "Dark Void", "Phantom Strike"],
  },
  crystal: {
    name: "CRYSTAL",
    color: "#00ffff",
    secondaryColor: "#40ffff",
    width: 52,
    height: 78,
    speed: 5,
    jump_power: 14,
    attack_power: 15,
    special_power: 35,
    description: "Crystalline warrior with defensive abilities",
    rarity: "rare",
    unlocked: false,
    cost: 750,
    abilities: ["Crystal Shield", "Shard Storm", "Diamond Slam"],
  },
  phoenix: {
    name: "PHOENIX",
    color: "#ff8000",
    secondaryColor: "#ffa040",
    width: 55,
    height: 85,
    speed: 7,
    jump_power: 24,
    attack_power: 13,
    special_power: 40,
    description: "Legendary fire bird with resurrection power",
    rarity: "legendary",
    unlocked: false,
    cost: 1500,
    abilities: ["Phoenix Rising", "Inferno Wings", "Rebirth"],
  },
  void: {
    name: "VOID",
    color: "#4000ff",
    secondaryColor: "#6040ff",
    width: 60,
    height: 90,
    speed: 4,
    jump_power: 12,
    attack_power: 20,
    special_power: 50,
    description: "Ancient entity from the cosmic void",
    rarity: "mythic",
    unlocked: false,
    cost: 3000,
    abilities: ["Black Hole", "Void Rift", "Cosmic Annihilation"],
  },
}

// Enhanced emotes system with 25 new emotes
const EMOTES = {
  // Victory & Celebration
  victory: { name: "VICTORY", icon: "🏆", cost: 100, unlocked: false },
  party: { name: "PARTY", icon: "🎉", cost: 120, unlocked: false },
  dance: { name: "DANCE", icon: "💃", cost: 150, unlocked: false },
  flex: { name: "FLEX", icon: "💪", cost: 80, unlocked: false },
  crown: { name: "CROWN", icon: "👑", cost: 300, unlocked: false },

  // Combat & Action
  fire: { name: "FIRE", icon: "🔥", cost: 90, unlocked: false },
  lightning: { name: "LIGHTNING", icon: "⚡", cost: 110, unlocked: false },
  explosion: { name: "EXPLOSION", icon: "💥", cost: 130, unlocked: false },
  sword: { name: "SWORD", icon: "⚔️", cost: 140, unlocked: false },
  shield: { name: "SHIELD", icon: "🛡️", cost: 120, unlocked: false },

  // Emotions & Reactions
  cool: { name: "COOL", icon: "😎", cost: 70, unlocked: false },
  angry: { name: "ANGRY", icon: "😡", cost: 60, unlocked: false },
  laugh: { name: "LAUGH", icon: "😂", cost: 80, unlocked: false },
  shocked: { name: "SHOCKED", icon: "😱", cost: 90, unlocked: false },
  smirk: { name: "SMIRK", icon: "😏", cost: 85, unlocked: false },

  // Gestures
  thumbsUp: { name: "THUMBS UP", icon: "👍", cost: 50, unlocked: false },
  thumbsDown: { name: "THUMBS DOWN", icon: "👎", cost: 50, unlocked: false },
  wave: { name: "WAVE", icon: "👋", cost: 40, unlocked: false },
  peace: { name: "PEACE", icon: "✌️", cost: 60, unlocked: false },
  fist: { name: "FIST BUMP", icon: "👊", cost: 70, unlocked: false },

  // Special & Rare
  star: { name: "STAR", icon: "⭐", cost: 200, unlocked: false },
  diamond: { name: "DIAMOND", icon: "💎", cost: 250, unlocked: false },
  rocket: { name: "ROCKET", icon: "🚀", cost: 180, unlocked: false },
  magic: { name: "MAGIC", icon: "✨", cost: 160, unlocked: false },
  skull: { name: "SKULL", icon: "💀", cost: 220, unlocked: false },
}

// Super attacks
const SUPER_ATTACKS = {
  meteor: { name: "METEOR STRIKE", cost: 800, unlocked: false, damage: 60 },
  tornado: { name: "TORNADO", cost: 600, unlocked: false, damage: 45 },
  earthquake: { name: "EARTHQUAKE", cost: 700, unlocked: false, damage: 50 },
  blizzard: { name: "BLIZZARD", cost: 900, unlocked: false, damage: 55 },
}

interface Player {
  character_key: string
  character_data: any
  player_num: number
  is_ai: boolean
  x: number
  y: number
  width: number
  height: number
  vel_x: number
  vel_y: number
  speed: number
  jump_power: number
  facing_right: boolean
  health: number
  attack_power: number
  special_power: number
  damage_taken: number
  on_ground: boolean
  attacking: boolean
  special_attacking: boolean
  hit_cooldown: number
  attack_cooldown: number
  special_cooldown: number
  stun_timer: number
  jumps_left: number
  animation_frame: number
  animation_timer: number
  animation_state: string
  ai_attack_chance: number
  ai_special_chance: number
  ai_jump_chance: number
  attack_hitbox: { x: number; y: number; width: number; height: number }
  attack_active: boolean
  emote_timer: number
  current_emote: string | null
}

interface GameData {
  username: string
  coins: number
  totalWins: number
  totalMatches: number
  unlockedCharacters: string[]
  unlockedEmotes: string[]
  unlockedSuperAttacks: string[]
  selectedCharacter: string
  gameMode: string
  keybinds: typeof DEFAULT_KEYBINDS
  settings: {
    soundEnabled: boolean
    musicEnabled: boolean
    difficulty: string
  }
}

interface Platform {
  x: number
  y: number
  width: number
  height: number
  color: string
  gradient?: boolean
}

interface Particle {
  x: number
  y: number
  color: string
  size: number
  velocity_x: number
  velocity_y: number
  lifetime: number
  age: number
  type: string
}

export default function ComboBros2D() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  const keysPressed = useRef<Set<string>>(new Set())

  const [gameState, setGameState] = useState<
    "menu" | "characterSelect" | "gameModeSelect" | "shop" | "profile" | "settings" | "keybinds" | "game" | "gameOver"
  >("menu")

  const [gameData, setGameData] = useState<GameData>({
    username: "",
    coins: 1000, // Starting coins
    totalWins: 0,
    totalMatches: 0,
    unlockedCharacters: ["blaze", "verdant", "nimbus"],
    unlockedEmotes: [],
    unlockedSuperAttacks: [],
    selectedCharacter: "blaze",
    gameMode: "classic",
    keybinds: DEFAULT_KEYBINDS,
    settings: {
      soundEnabled: true,
      musicEnabled: true,
      difficulty: "Normal",
    },
  })

  const [selectedCharacters, setSelectedCharacters] = useState<{ player1: string | null; player2: string | null }>({
    player1: null,
    player2: null,
  })
  const [winner, setWinner] = useState<string | null>(null)
  const [shopCategory, setShopCategory] = useState<"characters" | "emotes" | "superAttacks">("characters")
  const [showNotification, setShowNotification] = useState<{ message: string; type: string } | null>(null)
  const [bindingKey, setBindingKey] = useState<string | null>(null)

  // Animation states
  const [menuAnimation, setMenuAnimation] = useState(0)
  const [backgroundOffset, setBackgroundOffset] = useState(0)

  // Game objects
  const gameObjects = useRef<{
    player1: Player | null
    player2: Player | null
    platforms: Platform[]
    particles: Particle[]
    animationTimer: number
    lastTime: number
    mapName: string
    gameMode: string
    timeLimit: number
    currentTime: number
  }>({
    player1: null,
    player2: null,
    platforms: [],
    particles: [],
    animationTimer: 0,
    lastTime: 0,
    mapName: "CYBER ARENA (ONLINE)",
    gameMode: "classic",
    timeLimit: 180,
    currentTime: 0,
  })

  // Load game data from localStorage
  useEffect(() => {
    const savedData = localStorage.getItem("comboBros2D_gameData")
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData)
        setGameData((prev) => ({
          ...prev,
          ...parsed,
          keybinds: { ...DEFAULT_KEYBINDS, ...parsed.keybinds },
        }))
      } catch (error) {
        console.error("Failed to load game data:", error)
      }
    }
  }, [])

  // Save game data to localStorage
  const saveGameData = (data: Partial<GameData>) => {
    const newData = { ...gameData, ...data }
    setGameData(newData)
    localStorage.setItem("comboBros2D_gameData", JSON.stringify(newData))
  }

  // Show notification
  const showNotificationMessage = (message: string, type: "success" | "error" | "info" = "info") => {
    setShowNotification({ message, type })
    setTimeout(() => setShowNotification(null), 3000)
  }

  // Enhanced keyboard handling
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Handle keybind setting
      if (bindingKey) {
        e.preventDefault()
        const newKeybinds = { ...gameData.keybinds, [bindingKey]: e.code }
        saveGameData({ keybinds: newKeybinds })
        setBindingKey(null)
        showNotificationMessage(`Key bound to ${e.key.toUpperCase()}`, "success")
        return
      }

      // Handle ESC key
      if (e.code === "Escape") {
        if (gameState === "game") {
          setGameState("menu")
        } else if (gameState !== "menu") {
          setGameState("menu")
        }
        return
      }

      // Add key to pressed set for smooth movement
      keysPressed.current.add(e.code)
    }

    const handleKeyUp = (e: KeyboardEvent) => {
      keysPressed.current.delete(e.code)
    }

    window.addEventListener("keydown", handleKeyDown)
    window.addEventListener("keyup", handleKeyUp)

    return () => {
      window.removeEventListener("keydown", handleKeyDown)
      window.removeEventListener("keyup", handleKeyUp)
    }
  }, [gameState, gameData.keybinds, bindingKey])

  // Create enhanced character preview sprite for selection screen
  const createCharacterPreviewSprite = (character: any, size = 64) => {
    const canvas = document.createElement("canvas")
    canvas.width = size
    canvas.height = size
    const ctx = canvas.getContext("2d")!

    ctx.imageSmoothingEnabled = false

    // Character-specific sprite creation
    const pixelSize = Math.max(2, size / 16)

    // Head
    ctx.fillStyle = character.color
    ctx.fillRect(size * 0.25, size * 0.1, size * 0.5, size * 0.3)

    // Eyes
    ctx.fillStyle = "#ffffff"
    ctx.fillRect(size * 0.35, size * 0.2, pixelSize * 2, pixelSize)
    ctx.fillRect(size * 0.55, size * 0.2, pixelSize * 2, pixelSize)

    // Body
    ctx.fillStyle = character.color
    ctx.fillRect(size * 0.3, size * 0.4, size * 0.4, size * 0.35)

    // Body accent
    ctx.fillStyle = character.secondaryColor
    ctx.fillRect(size * 0.35, size * 0.45, size * 0.3, size * 0.2)

    // Arms
    ctx.fillStyle = character.color
    ctx.fillRect(size * 0.15, size * 0.45, size * 0.15, size * 0.25)
    ctx.fillRect(size * 0.7, size * 0.45, size * 0.15, size * 0.25)

    // Legs
    ctx.fillRect(size * 0.35, size * 0.75, size * 0.12, size * 0.2)
    ctx.fillRect(size * 0.53, size * 0.75, size * 0.12, size * 0.2)

    // Character-specific details
    if (character.name === "BLAZE") {
      // Fire effect
      ctx.fillStyle = "#ff8000"
      ctx.fillRect(size * 0.2, size * 0.05, pixelSize, pixelSize)
      ctx.fillRect(size * 0.75, size * 0.08, pixelSize, pixelSize)
    } else if (character.name === "VERDANT") {
      // Leaf details
      ctx.fillStyle = "#00aa00"
      ctx.fillRect(size * 0.25, size * 0.35, pixelSize, pixelSize)
      ctx.fillRect(size * 0.7, size * 0.38, pixelSize, pixelSize)
    } else if (character.name === "NIMBUS") {
      // Cloud wisps
      ctx.fillStyle = "#ffffff"
      ctx.fillRect(size * 0.15, size * 0.25, pixelSize, pixelSize)
      ctx.fillRect(size * 0.8, size * 0.3, pixelSize, pixelSize)
    } else if (character.name === "SHADOW") {
      // Dark aura
      ctx.fillStyle = "#4000aa"
      ctx.fillRect(size * 0.1, size * 0.2, pixelSize, pixelSize)
      ctx.fillRect(size * 0.85, size * 0.25, pixelSize, pixelSize)
    } else if (character.name === "CRYSTAL") {
      // Crystal shards
      ctx.fillStyle = "#80ffff"
      ctx.fillRect(size * 0.2, size * 0.15, pixelSize, pixelSize)
      ctx.fillRect(size * 0.75, size * 0.18, pixelSize, pixelSize)
    } else if (character.name === "PHOENIX") {
      // Fire wings
      ctx.fillStyle = "#ffaa00"
      ctx.fillRect(size * 0.05, size * 0.4, pixelSize * 2, pixelSize)
      ctx.fillRect(size * 0.85, size * 0.4, pixelSize * 2, pixelSize)
    } else if (character.name === "VOID") {
      // Void particles
      ctx.fillStyle = "#8000ff"
      ctx.fillRect(size * 0.1, size * 0.1, pixelSize, pixelSize)
      ctx.fillRect(size * 0.85, size * 0.15, pixelSize, pixelSize)
      ctx.fillRect(size * 0.15, size * 0.85, pixelSize, pixelSize)
    }

    return canvas
  }

  // Create enhanced pixelated character sprite with retro style
  const createEnhancedCharacterSprite = (
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    character: any,
    animationFrame = 0,
  ) => {
    const canvas = document.createElement("canvas")
    canvas.width = width
    canvas.height = height
    const spriteCtx = canvas.getContext("2d")!

    const pixelSize = Math.max(3, Math.min(width, height) / 10)
    const headHeight = height * 0.25
    const bodyHeight = height * 0.4

    // Retro pixelated style
    spriteCtx.imageSmoothingEnabled = false

    // Animated breathing effect
    const breatheOffset = Math.sin(animationFrame * 0.1) * 1

    // Draw pixelated head with neon glow
    const headRadius = (width * 0.6) / 2
    const headCenterX = width / 2
    const headCenterY = headHeight / 2 + breatheOffset

    // Neon glow effect
    spriteCtx.shadowColor = character.color
    spriteCtx.shadowBlur = 8
    spriteCtx.fillStyle = character.color
    spriteCtx.fillRect(headCenterX - headRadius, headCenterY - headRadius, headRadius * 2, headRadius * 2)

    // Reset shadow
    spriteCtx.shadowBlur = 0

    // Pixelated body
    const bodyY = headHeight + breatheOffset
    spriteCtx.fillStyle = character.color
    spriteCtx.fillRect(width * 0.25, bodyY, width * 0.5, bodyHeight)

    // Body details with secondary color
    spriteCtx.fillStyle = character.secondaryColor || character.color
    spriteCtx.fillRect(width * 0.3, bodyY + bodyHeight * 0.2, width * 0.4, bodyHeight * 0.3)

    // Pixelated arms
    spriteCtx.fillStyle = character.color
    spriteCtx.fillRect(width * 0.1, bodyY + bodyHeight * 0.1, width * 0.15, bodyHeight * 0.6)
    spriteCtx.fillRect(width * 0.75, bodyY + bodyHeight * 0.1, width * 0.15, bodyHeight * 0.6)

    // Pixelated legs
    const legsY = headHeight + bodyHeight + breatheOffset
    spriteCtx.fillStyle = character.color
    spriteCtx.fillRect(width * 0.3, legsY, width * 0.15, height - legsY)
    spriteCtx.fillRect(width * 0.55, legsY, width * 0.15, height - legsY)

    // Glowing pixelated eyes
    spriteCtx.shadowColor = COLORS.neon.cyan
    spriteCtx.shadowBlur = 4
    spriteCtx.fillStyle = COLORS.neon.cyan
    const eyeSize = Math.max(3, pixelSize)
    spriteCtx.fillRect(width * 0.4, headHeight * 0.4 + breatheOffset, eyeSize, eyeSize)
    spriteCtx.fillRect(width * 0.6, headHeight * 0.4 + breatheOffset, eyeSize, eyeSize)

    spriteCtx.shadowBlur = 0

    return canvas
  }

  // Create player
  const createPlayer = (characterKey: string, playerNum: number, isAI = false): Player => {
    const charData = CHARACTERS[characterKey as keyof typeof CHARACTERS]
    return {
      character_key: characterKey,
      character_data: charData,
      player_num: playerNum,
      is_ai: isAI,
      x: playerNum === 1 ? SCREEN_WIDTH / 4 : (3 * SCREEN_WIDTH) / 4,
      y: GROUND_Y - charData.height,
      width: charData.width,
      height: charData.height,
      vel_x: 0,
      vel_y: 0,
      speed: charData.speed,
      jump_power: charData.jump_power,
      facing_right: playerNum === 1,
      health: MAX_HEALTH,
      attack_power: charData.attack_power,
      special_power: charData.special_power,
      damage_taken: 0,
      on_ground: true,
      attacking: false,
      special_attacking: false,
      hit_cooldown: 0,
      attack_cooldown: 0,
      special_cooldown: 0,
      stun_timer: 0,
      jumps_left: 2,
      animation_frame: 0,
      animation_timer: 0,
      animation_state: "idle",
      ai_attack_chance: 0.1,
      ai_special_chance: 0.02,
      ai_jump_chance: 0.02,
      attack_hitbox: { x: 0, y: 0, width: 0, height: 0 },
      attack_active: false,
      emote_timer: 0,
      current_emote: null,
    }
  }

  // Generate retro map
  const generateModernMap = (gameMode: string) => {
    const platforms: Platform[] = []

    // Different platform layouts based on game mode
    const platformConfigs = {
      classic: [
        { x: SCREEN_WIDTH * 0.2, y: GROUND_Y - 150, width: 200, height: PLATFORM_HEIGHT },
        { x: SCREEN_WIDTH * 0.6, y: GROUND_Y - 150, width: 200, height: PLATFORM_HEIGHT },
        { x: SCREEN_WIDTH * 0.4, y: GROUND_Y - 250, width: 150, height: PLATFORM_HEIGHT },
      ],
      survival: [
        { x: SCREEN_WIDTH * 0.1, y: GROUND_Y - 100, width: 150, height: PLATFORM_HEIGHT },
        { x: SCREEN_WIDTH * 0.35, y: GROUND_Y - 200, width: 300, height: PLATFORM_HEIGHT },
        { x: SCREEN_WIDTH * 0.75, y: GROUND_Y - 100, width: 150, height: PLATFORM_HEIGHT },
        { x: SCREEN_WIDTH * 0.45, y: GROUND_Y - 350, width: 100, height: PLATFORM_HEIGHT },
      ],
      timeAttack: [
        { x: SCREEN_WIDTH * 0.25, y: GROUND_Y - 120, width: 180, height: PLATFORM_HEIGHT },
        { x: SCREEN_WIDTH * 0.55, y: GROUND_Y - 120, width: 180, height: PLATFORM_HEIGHT },
      ],
      tournament: [
        { x: SCREEN_WIDTH * 0.15, y: GROUND_Y - 180, width: 160, height: PLATFORM_HEIGHT },
        { x: SCREEN_WIDTH * 0.65, y: GROUND_Y - 180, width: 160, height: PLATFORM_HEIGHT },
        { x: SCREEN_WIDTH * 0.4, y: GROUND_Y - 300, width: 200, height: PLATFORM_HEIGHT },
      ],
    }

    const config = platformConfigs[gameMode as keyof typeof platformConfigs] || platformConfigs.classic

    config.forEach((platform, index) => {
      platforms.push({
        ...platform,
        color: COLORS.neon.green,
        gradient: true,
      })
    })

    // Add ground platform
    platforms.push({
      x: 0,
      y: GROUND_Y,
      width: SCREEN_WIDTH,
      height: PLATFORM_HEIGHT,
      color: COLORS.neon.green,
      gradient: true,
    })

    const mapNames = {
      classic: "CYBER ARENA (CLASSIC)",
      survival: "NEON BATTLEGROUND",
      timeAttack: "SPEED ZONE",
      tournament: "CHAMPIONSHIP STAGE",
      practice: "TRAINING GROUNDS",
    }

    return {
      platforms,
      mapName: mapNames[gameMode as keyof typeof mapNames] || "CYBER ARENA (CLASSIC)",
    }
  }

  // Enhanced retro background
  const drawModernBackground = (ctx: CanvasRenderingContext2D, timer: number, mapName: string) => {
    // Black background
    ctx.fillStyle = COLORS.retro.bg
    ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    // Animated neon grid
    ctx.strokeStyle = `${COLORS.neon.green}40`
    ctx.lineWidth = 1
    const gridSize = 40
    const offsetX = (timer * 0.3) % gridSize
    const offsetY = (timer * 0.2) % gridSize

    for (let x = -offsetX; x < SCREEN_WIDTH + gridSize; x += gridSize) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, SCREEN_HEIGHT)
      ctx.stroke()
    }

    for (let y = -offsetY; y < SCREEN_HEIGHT + gridSize; y += gridSize) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(SCREEN_WIDTH, y)
      ctx.stroke()
    }

    // Floating neon particles
    for (let i = 0; i < 20; i++) {
      const x = ((timer * (0.3 + i * 0.05) + i * 80) % (SCREEN_WIDTH + 80)) - 40
      const y = (i * 40 + Math.sin(timer * 0.008 + i) * 15) % SCREEN_HEIGHT
      const size = 2 + Math.sin(timer * 0.04 + i) * 1
      const alpha = 0.4 + Math.sin(timer * 0.02 + i) * 0.3

      const colors = [COLORS.neon.green, COLORS.neon.pink, COLORS.neon.cyan]
      const color = colors[i % colors.length]

      ctx.fillStyle = `${color}${Math.floor(alpha * 255)
        .toString(16)
        .padStart(2, "0")}`
      ctx.fillRect(x, y, size, size)
    }

    // Map name with retro styling
    ctx.save()
    ctx.shadowColor = COLORS.neon.green
    ctx.shadowBlur = 15
    ctx.fillStyle = COLORS.neon.green
    ctx.font = "bold 24px 'Courier New', monospace"
    ctx.textAlign = "right"
    ctx.fillText(mapName, SCREEN_WIDTH - 20, 40)
    ctx.restore()
  }

  // Enhanced retro platform drawing
  const drawModernPlatform = (ctx: CanvasRenderingContext2D, platform: Platform) => {
    // Neon glow effect
    ctx.shadowColor = platform.color
    ctx.shadowBlur = 8
    ctx.fillStyle = platform.color
    ctx.fillRect(platform.x, platform.y, platform.width, platform.height)

    // Add scanlines for retro effect
    ctx.shadowBlur = 0
    ctx.strokeStyle = `${platform.color}80`
    ctx.lineWidth = 1
    for (let y = platform.y; y < platform.y + platform.height; y += 2) {
      ctx.beginPath()
      ctx.moveTo(platform.x, y)
      ctx.lineTo(platform.x + platform.width, y)
      ctx.stroke()
    }
  }

  // Enhanced retro player drawing
  const drawModernPlayer = (ctx: CanvasRenderingContext2D, player: Player) => {
    // Create enhanced sprite
    const sprite = createEnhancedCharacterSprite(
      ctx,
      player.width,
      player.height,
      player.character_data,
      player.animation_frame,
    )

    // Flash when hit with retro effect
    if (player.hit_cooldown > 0) {
      ctx.save()
      ctx.globalAlpha = 0.6 + Math.sin(player.hit_cooldown * 0.8) * 0.4
      ctx.filter = "brightness(200%) saturate(200%)"
    }

    ctx.drawImage(sprite, player.x, player.y)

    if (player.hit_cooldown > 0) {
      ctx.restore()
    }

    // Enhanced attack effects with retro style
    if (player.attacking) {
      ctx.save()
      ctx.shadowColor = player.character_data.color
      ctx.shadowBlur = 12
      ctx.strokeStyle = player.character_data.color
      ctx.lineWidth = 3
      ctx.strokeRect(player.x - 10, player.y - 10, player.width + 20, player.height + 20)
      ctx.restore()
    }

    // Special attack effects
    if (player.special_attacking) {
      const time = player.animation_timer * 0.1

      if (player.character_key === "blaze") {
        // Retro fire nova
        for (let i = 0; i < 8; i++) {
          const angle = i * ((Math.PI * 2) / 8) + time
          const radius = 50 + 20 * Math.sin(time * 3)
          const x = player.x + player.width / 2 + radius * Math.cos(angle)
          const y = player.y + player.height / 2 + radius * Math.sin(angle)

          ctx.save()
          ctx.shadowColor = COLORS.neon.orange
          ctx.shadowBlur = 8
          ctx.fillStyle = COLORS.neon.orange
          ctx.fillRect(x - 4, y - 4, 8, 8)
          ctx.restore()
        }
      }
    }

    // Retro health bar
    const healthBarWidth = 80
    const healthBarHeight = 6
    const healthBarX = player.x + player.width / 2 - healthBarWidth / 2
    const healthBarY = player.y - 30

    // Health bar background
    ctx.fillStyle = COLORS.retro.border
    ctx.fillRect(healthBarX, healthBarY, healthBarWidth, healthBarHeight)

    // Health bar fill
    const healthPercent = player.health / MAX_HEALTH
    let healthColor = COLORS.neon.green
    if (healthPercent < 0.6) healthColor = COLORS.neon.yellow
    if (healthPercent < 0.3) healthColor = COLORS.neon.pink

    ctx.save()
    ctx.shadowColor = healthColor
    ctx.shadowBlur = 4
    ctx.fillStyle = healthColor
    ctx.fillRect(healthBarX, healthBarY, healthBarWidth * healthPercent, healthBarHeight)
    ctx.restore()

    // Player indicator
    ctx.save()
    ctx.shadowColor = player.player_num === 1 ? COLORS.neon.pink : COLORS.neon.cyan
    ctx.shadowBlur = 8
    ctx.fillStyle = player.player_num === 1 ? COLORS.neon.pink : COLORS.neon.cyan
    ctx.fillRect(player.x + player.width / 2 - 3, player.y - 15, 6, 6)
    ctx.restore()

    // Damage percentage with retro font
    ctx.save()
    ctx.shadowColor = COLORS.light
    ctx.shadowBlur = 4
    ctx.fillStyle = COLORS.light
    ctx.font = "bold 14px 'Courier New', monospace"
    ctx.textAlign = "center"
    ctx.fillText(`${Math.floor(player.damage_taken)}%`, player.x + player.width / 2, player.y - 45)
    ctx.restore()

    // Show emote if active
    if (player.current_emote && player.emote_timer > 0) {
      ctx.font = "24px Arial"
      ctx.textAlign = "center"
      ctx.fillText(player.current_emote, player.x + player.width / 2, player.y - 60)
    }
  }

  // Update player with improved controls
  const updatePlayer = (player: Player, opponent: Player, platforms: Platform[], dt: number) => {
    // Handle player input with improved responsiveness
    if (!player.is_ai && player.stun_timer <= 0) {
      const kb = gameData.keybinds

      // Movement with immediate response
      if (keysPressed.current.has(kb.left)) {
        player.vel_x = -player.speed
        player.facing_right = false
      } else if (keysPressed.current.has(kb.right)) {
        player.vel_x = player.speed
        player.facing_right = true
      }

      // Jump
      if (keysPressed.current.has(kb.up) && player.jumps_left > 0) {
        player.vel_y = -player.jump_power
        player.jumps_left--
        player.on_ground = false
        keysPressed.current.delete(kb.up) // Prevent continuous jumping
      }

      // Attack
      if (keysPressed.current.has(kb.attack) && player.attack_cooldown <= 0) {
        player.attacking = true
        player.attack_active = true
        player.attack_cooldown = 15
        keysPressed.current.delete(kb.attack)
      }

      // Special attack
      if (keysPressed.current.has(kb.special) && player.special_cooldown <= 0) {
        player.special_attacking = true
        player.special_cooldown = 45
        keysPressed.current.delete(kb.special)
      }

      // Emotes - check for unlocked emotes
      if (keysPressed.current.has(kb.emote1)) {
        const unlockedEmoteKeys = Object.keys(EMOTES).filter((key) => gameData.unlockedEmotes.includes(key))
        if (unlockedEmoteKeys.length > 0) {
          const emoteKey = unlockedEmoteKeys[0]
          player.current_emote = EMOTES[emoteKey as keyof typeof EMOTES].icon
          player.emote_timer = 90
        }
        keysPressed.current.delete(kb.emote1)
      }
      if (keysPressed.current.has(kb.emote2)) {
        const unlockedEmoteKeys = Object.keys(EMOTES).filter((key) => gameData.unlockedEmotes.includes(key))
        if (unlockedEmoteKeys.length > 1) {
          const emoteKey = unlockedEmoteKeys[1]
          player.current_emote = EMOTES[emoteKey as keyof typeof EMOTES].icon
          player.emote_timer = 90
        }
        keysPressed.current.delete(kb.emote2)
      }
      if (keysPressed.current.has(kb.emote3)) {
        const unlockedEmoteKeys = Object.keys(EMOTES).filter((key) => gameData.unlockedEmotes.includes(key))
        if (unlockedEmoteKeys.length > 2) {
          const emoteKey = unlockedEmoteKeys[2]
          player.current_emote = EMOTES[emoteKey as keyof typeof EMOTES].icon
          player.emote_timer = 90
        }
        keysPressed.current.delete(kb.emote3)
      }
    }

    // Apply gravity
    if (!player.on_ground) {
      player.vel_y += GRAVITY * dt * 60
    }

    // Apply friction
    player.vel_x *= FRICTION

    // Update position
    player.x += player.vel_x * dt * 60
    player.y += player.vel_y * dt * 60

    // Boundaries
    if (player.x < 0) {
      player.x = 0
      player.vel_x = 0
    } else if (player.x > SCREEN_WIDTH - player.width) {
      player.x = SCREEN_WIDTH - player.width
      player.vel_x = 0
    }

    // Ground collision
    player.on_ground = false
    if (player.y >= GROUND_Y - player.height) {
      player.y = GROUND_Y - player.height
      player.vel_y = 0
      player.on_ground = true
      player.jumps_left = 2
    }

    // Platform collisions
    for (const platform of platforms) {
      if (
        player.vel_y > 0 &&
        player.y + player.height >= platform.y &&
        player.y + player.height <= platform.y + PLATFORM_HEIGHT &&
        player.x + player.width > platform.x &&
        player.x < platform.x + platform.width
      ) {
        player.y = platform.y - player.height
        player.vel_y = 0
        player.on_ground = true
        player.jumps_left = 2
      }
    }

    // Update cooldowns
    if (player.hit_cooldown > 0) player.hit_cooldown -= dt * 60
    if (player.attack_cooldown > 0) {
      player.attack_cooldown -= dt * 60
      if (player.attack_cooldown <= 0) {
        player.attacking = false
        player.attack_active = false
      }
    }
    if (player.special_cooldown > 0) {
      player.special_cooldown -= dt * 60
      if (player.special_cooldown <= 0) {
        player.special_attacking = false
      }
    }
    if (player.stun_timer > 0) player.stun_timer -= dt * 60
    if (player.emote_timer > 0) {
      player.emote_timer -= dt * 60
      if (player.emote_timer <= 0) {
        player.current_emote = null
      }
    }

    // Combat system
    if ((player.attacking || player.special_attacking) && player.attack_active) {
      if (player.attacking) {
        const hitboxWidth = player.width * 1.5
        const hitboxHeight = player.height * 0.6

        if (player.facing_right) {
          player.attack_hitbox = {
            x: player.x + player.width * 0.8,
            y: player.y + player.height * 0.2,
            width: hitboxWidth,
            height: hitboxHeight,
          }
        } else {
          player.attack_hitbox = {
            x: player.x - hitboxWidth * 0.8,
            y: player.y + player.height * 0.2,
            width: hitboxWidth,
            height: hitboxHeight,
          }
        }
      }

      // Check collision with opponent
      if (
        opponent.x < player.attack_hitbox.x + player.attack_hitbox.width &&
        opponent.x + opponent.width > player.attack_hitbox.x &&
        opponent.y < player.attack_hitbox.y + player.attack_hitbox.height &&
        opponent.y + opponent.height > player.attack_hitbox.y
      ) {
        if (opponent.hit_cooldown <= 0) {
          let damage = player.attacking ? player.attack_power : player.special_power
          damage *= 1 + player.damage_taken / 100

          let knockbackX = player.attacking ? 12 : 18
          const knockbackY = player.attacking ? -10 : -12

          if (!player.facing_right) knockbackX *= -1

          // Apply hit
          opponent.damage_taken += damage
          opponent.health = Math.max(0, MAX_HEALTH - opponent.damage_taken)

          const knockbackMultiplier = 1 + opponent.damage_taken / 50
          opponent.vel_x = knockbackX * knockbackMultiplier
          opponent.vel_y = knockbackY * knockbackMultiplier

          opponent.stun_timer = damage * 1.5
          opponent.hit_cooldown = 25

          player.attack_active = false
        }
      }
    }

    // Enhanced AI logic
    if (player.is_ai && opponent && player.stun_timer <= 0) {
      const distanceX = opponent.x - player.x
      const distanceY = opponent.y - player.y

      player.facing_right = distanceX > 0

      // Move toward opponent
      if (Math.abs(distanceX) > 80) {
        if (distanceX > 0) {
          player.vel_x = player.speed * dt * 60
        } else {
          player.vel_x = -player.speed * dt * 60
        }
      }

      // Jump
      if (
        (distanceY < -40 || (Math.abs(distanceX) < 150 && Math.random() < player.ai_jump_chance * dt * 60)) &&
        player.jumps_left > 0
      ) {
        player.vel_y = -player.jump_power
        player.jumps_left--
        player.on_ground = false
      }

      // Attack
      if (Math.abs(distanceX) < 100 && Math.abs(distanceY) < 60) {
        if (Math.random() < player.ai_attack_chance * dt * 60 && player.attack_cooldown <= 0) {
          player.attacking = true
          player.attack_active = true
          player.attack_cooldown = 15
        } else if (Math.random() < player.ai_special_chance * dt * 60 && player.special_cooldown <= 0) {
          player.special_attacking = true
          player.special_cooldown = 45
        }
      }

      // Random emotes for AI
      if (Math.random() < 0.0008 && player.emote_timer <= 0) {
        const emotes = ["👍", "🔥", "⚡", "💪"]
        player.current_emote = emotes[Math.floor(Math.random() * emotes.length)]
        player.emote_timer = 90
      }
    }

    // Update animation
    player.animation_timer += dt * 60
    if (player.animation_timer >= 8) {
      player.animation_timer = 0
      player.animation_frame = (player.animation_frame + 1) % 6
    }
  }

  // Game loop with enhanced features
  const gameLoop = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const currentTime = performance.now()
    const dt = Math.min((currentTime - gameObjects.current.lastTime) / 1000, 0.1)
    gameObjects.current.lastTime = currentTime
    gameObjects.current.animationTimer++

    // Update background animation
    setBackgroundOffset((prev) => prev + dt * 15)

    if (gameState === "game" && gameObjects.current.player1 && gameObjects.current.player2) {
      // Update game timer
      gameObjects.current.currentTime += dt

      // Update players
      updatePlayer(gameObjects.current.player1, gameObjects.current.player2, gameObjects.current.platforms, dt)
      updatePlayer(gameObjects.current.player2, gameObjects.current.player1, gameObjects.current.platforms, dt)

      // Check win conditions
      let gameEnded = false
      let winReason = ""

      if (gameObjects.current.player1.health <= 0) {
        setWinner(gameObjects.current.player2.character_data.name)
        winReason = "KO"
        gameEnded = true
      } else if (gameObjects.current.player2.health <= 0) {
        setWinner(gameObjects.current.player1.character_data.name)
        winReason = "KO"
        gameEnded = true
      } else if (
        gameObjects.current.gameMode === "timeAttack" &&
        gameObjects.current.currentTime >= gameObjects.current.timeLimit
      ) {
        // Time attack mode - winner is player with more health
        if (gameObjects.current.player1.health > gameObjects.current.player2.health) {
          setWinner(gameObjects.current.player1.character_data.name)
        } else if (gameObjects.current.player2.health > gameObjects.current.player1.health) {
          setWinner(gameObjects.current.player2.character_data.name)
        } else {
          setWinner("Draw")
        }
        winReason = "Time Up"
        gameEnded = true
      }

      if (gameEnded) {
        // Award coins and update stats
        const modeCoins = GAME_MODES[gameObjects.current.gameMode as keyof typeof GAME_MODES]?.coins || 50
        const wonMatch = winner !== "Draw" && winner === gameObjects.current.player1.character_data.name

        saveGameData({
          coins: gameData.coins + (wonMatch ? modeCoins : Math.floor(modeCoins / 2)),
          totalMatches: gameData.totalMatches + 1,
          totalWins: gameData.totalWins + (wonMatch ? 1 : 0),
        })

        setGameState("gameOver")
      }

      // Draw everything
      ctx.clearRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
      drawModernBackground(ctx, gameObjects.current.animationTimer, gameObjects.current.mapName)

      // Draw platforms
      for (const platform of gameObjects.current.platforms) {
        drawModernPlatform(ctx, platform)
      }

      // Draw players
      drawModernPlayer(ctx, gameObjects.current.player1)
      drawModernPlayer(ctx, gameObjects.current.player2)

      // Draw retro UI
      drawModernGameUI(ctx)
    }

    animationRef.current = requestAnimationFrame(gameLoop)
  }

  // Retro game UI
  const drawModernGameUI = (ctx: CanvasRenderingContext2D) => {
    // Time display for time attack mode
    if (gameObjects.current.gameMode === "timeAttack") {
      const timeLeft = Math.max(0, gameObjects.current.timeLimit - gameObjects.current.currentTime)
      const minutes = Math.floor(timeLeft / 60)
      const seconds = Math.floor(timeLeft % 60)

      ctx.save()
      ctx.shadowColor = COLORS.neon.yellow
      ctx.shadowBlur = 8
      ctx.fillStyle = COLORS.neon.yellow
      ctx.font = "bold 28px 'Courier New', monospace"
      ctx.textAlign = "center"
      ctx.fillText(`${minutes}:${seconds.toString().padStart(2, "0")}`, SCREEN_WIDTH / 2, 40)
      ctx.restore()
    }

    // Game mode indicator
    ctx.save()
    ctx.shadowColor = COLORS.neon.green
    ctx.shadowBlur = 6
    ctx.strokeStyle = COLORS.neon.green
    ctx.lineWidth = 2
    ctx.strokeRect(15, 15, 180, 30)

    ctx.fillStyle = COLORS.neon.green
    ctx.font = "bold 14px 'Courier New', monospace"
    ctx.textAlign = "left"
    ctx.fillText(`${GAME_MODES[gameObjects.current.gameMode as keyof typeof GAME_MODES]?.name || "CLASSIC"}`, 25, 35)
    ctx.restore()

    // Player names with retro styling
    if (gameObjects.current.player1 && gameObjects.current.player2) {
      ctx.save()
      ctx.font = "bold 16px 'Courier New', monospace"

      // Player 1
      ctx.shadowColor = COLORS.neon.pink
      ctx.shadowBlur = 6
      ctx.fillStyle = COLORS.neon.pink
      ctx.textAlign = "left"
      ctx.fillText(`P1: ${gameObjects.current.player1.character_data.name}`, 20, SCREEN_HEIGHT - 40)

      // Player 2
      ctx.shadowColor = COLORS.neon.cyan
      ctx.shadowBlur = 6
      ctx.fillStyle = COLORS.neon.cyan
      ctx.textAlign = "right"
      ctx.fillText(`P2: ${gameObjects.current.player2.character_data.name}`, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 40)
      ctx.restore()
    }
  }

  // Start game loop
  useEffect(() => {
    gameObjects.current.lastTime = performance.now()
    animationRef.current = requestAnimationFrame(gameLoop)

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [gameState])

  // Menu animation
  useEffect(() => {
    const interval = setInterval(() => {
      setMenuAnimation((prev) => prev + 1)
    }, 50)
    return () => clearInterval(interval)
  }, [])

  // Start game
  const startGame = () => {
    if (!selectedCharacters.player1 || !selectedCharacters.player2) return

    const player1 = createPlayer(selectedCharacters.player1, 1, false)
    const player2 = createPlayer(selectedCharacters.player2, 2, true)

    // Apply difficulty settings
    if (gameData.settings.difficulty === "Easy") {
      player2.speed *= 0.6
      player2.attack_power *= 0.7
      player2.ai_attack_chance = 0.04
    } else if (gameData.settings.difficulty === "Hard") {
      player2.speed *= 1.3
      player2.attack_power *= 1.3
      player2.ai_attack_chance = 0.18
    } else if (gameData.settings.difficulty === "Insane") {
      player2.speed *= 1.6
      player2.attack_power *= 1.6
      player2.ai_attack_chance = 0.25
    }

    const { platforms, mapName } = generateModernMap(gameData.gameMode)

    gameObjects.current.player1 = player1
    gameObjects.current.player2 = player2
    gameObjects.current.platforms = platforms
    gameObjects.current.mapName = mapName
    gameObjects.current.gameMode = gameData.gameMode
    gameObjects.current.animationTimer = 0
    gameObjects.current.currentTime = 0

    // Set time limit for time attack mode
    if (gameData.gameMode === "timeAttack") {
      gameObjects.current.timeLimit = 120 // 2 minutes
    }

    setGameState("game")
  }

  // Shop functions
  const purchaseItem = (category: string, itemKey: string, cost: number) => {
    if (gameData.coins < cost) {
      showNotificationMessage("NOT ENOUGH COINS!", "error")
      return
    }

    const updateData: Partial<GameData> = { coins: gameData.coins - cost }

    if (category === "characters") {
      updateData.unlockedCharacters = [...gameData.unlockedCharacters, itemKey]
    } else if (category === "emotes") {
      updateData.unlockedEmotes = [...gameData.unlockedEmotes, itemKey]
    } else if (category === "superAttacks") {
      updateData.unlockedSuperAttacks = [...gameData.unlockedSuperAttacks, itemKey]
    }

    saveGameData(updateData)
    showNotificationMessage("PURCHASE SUCCESSFUL!", "success")
  }

  // Get key name for display
  const getKeyName = (code: string) => {
    const keyMap: { [key: string]: string } = {
      KeyW: "W",
      KeyA: "A",
      KeyS: "S",
      KeyD: "D",
      KeyF: "F",
      KeyG: "G",
      Digit1: "1",
      Digit2: "2",
      Digit3: "3",
      Space: "SPACE",
      ArrowUp: "↑",
      ArrowDown: "↓",
      ArrowLeft: "←",
      ArrowRight: "→",
    }
    return keyMap[code] || code.replace("Key", "").replace("Digit", "")
  }

  // Render different screens
  const renderScreen = () => {
    switch (gameState) {
      case "menu":
        return (
          <div className="min-h-screen bg-black text-green-400 overflow-hidden relative font-mono">
            {/* Animated retro background */}
            <div className="absolute inset-0">
              <div className="absolute inset-0 bg-gradient-to-b from-green-900/10 to-black" />
              {/* Animated scanlines */}
              <div
                className="absolute inset-0 opacity-20"
                style={{
                  background: `repeating-linear-gradient(0deg, transparent, transparent 2px, #00ff41 2px, #00ff41 4px)`,
                  transform: `translateY(${(menuAnimation * 0.5) % 4}px)`,
                }}
              />
            </div>

            <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-8">
              {/* Retro title */}
              <div className="text-center mb-12">
                <div className="relative">
                  <h1
                    className="text-8xl font-bold mb-4 text-green-400"
                    style={{
                      textShadow: "0 0 20px #00ff41, 0 0 40px #00ff41",
                      transform: `scale(${1 + Math.sin(menuAnimation * 0.02) * 0.03})`,
                    }}
                  >
                    COMBO BROS 2D
                  </h1>
                  <div className="absolute inset-0 text-8xl font-bold text-green-400/20 blur-sm">COMBO BROS 2D</div>
                </div>
                <p className="text-xl text-green-300 font-light tracking-wider">&gt; RETRO FIGHTING EXPERIENCE &lt;</p>
              </div>

              {/* Stats display with retro styling */}
              <div className="flex space-x-8 mb-8 text-center">
                <div className="bg-black border-2 border-green-400 p-4 relative">
                  <div className="absolute inset-0 bg-green-400/10" />
                  <div className="relative">
                    <div className="text-3xl font-bold text-yellow-400" style={{ textShadow: "0 0 10px #ffff00" }}>
                      {gameData.coins}
                    </div>
                    <div className="text-sm text-green-300">COINS</div>
                  </div>
                </div>
                <div className="bg-black border-2 border-green-400 p-4 relative">
                  <div className="absolute inset-0 bg-green-400/10" />
                  <div className="relative">
                    <div className="text-3xl font-bold text-green-400" style={{ textShadow: "0 0 10px #00ff41" }}>
                      {gameData.totalWins}
                    </div>
                    <div className="text-sm text-green-300">WINS</div>
                  </div>
                </div>
                <div className="bg-black border-2 border-green-400 p-4 relative">
                  <div className="absolute inset-0 bg-green-400/10" />
                  <div className="relative">
                    <div className="text-3xl font-bold text-cyan-400" style={{ textShadow: "0 0 10px #00ffff" }}>
                      {gameData.totalMatches}
                    </div>
                    <div className="text-sm text-green-300">MATCHES</div>
                  </div>
                </div>
              </div>

              {/* Retro menu buttons */}
              <div className="grid grid-cols-2 gap-6 mb-8">
                <button
                  onClick={() => setGameState("gameModeSelect")}
                  className="group relative px-8 py-6 bg-black border-2 border-red-400 hover:bg-red-400/20 transition-all duration-300 transform hover:scale-105"
                  style={{ textShadow: "0 0 10px #ff0040" }}
                >
                  <div className="text-2xl font-bold mb-2 text-red-400">► PLAY GAME</div>
                  <div className="text-sm text-red-300">START YOUR BATTLE</div>
                </button>

                <button
                  onClick={() => setGameState("shop")}
                  className="group relative px-8 py-6 bg-black border-2 border-purple-400 hover:bg-purple-400/20 transition-all duration-300 transform hover:scale-105"
                  style={{ textShadow: "0 0 10px #8000ff" }}
                >
                  <div className="text-2xl font-bold mb-2 text-purple-400">► SHOP</div>
                  <div className="text-sm text-purple-300">BUY CHARACTERS & ITEMS</div>
                </button>

                <button
                  onClick={() => setGameState("profile")}
                  className="group relative px-8 py-6 bg-black border-2 border-cyan-400 hover:bg-cyan-400/20 transition-all duration-300 transform hover:scale-105"
                  style={{ textShadow: "0 0 10px #00ffff" }}
                >
                  <div className="text-2xl font-bold mb-2 text-cyan-400">► PROFILE</div>
                  <div className="text-sm text-cyan-300">VIEW YOUR STATS</div>
                </button>

                <button
                  onClick={() => setGameState("settings")}
                  className="group relative px-8 py-6 bg-black border-2 border-yellow-400 hover:bg-yellow-400/20 transition-all duration-300 transform hover:scale-105"
                  style={{ textShadow: "0 0 10px #ffff00" }}
                >
                  <div className="text-2xl font-bold mb-2 text-yellow-400">► SETTINGS</div>
                  <div className="text-sm text-yellow-300">GAME PREFERENCES</div>
                </button>
              </div>

              {/* Username display */}
              {gameData.username && (
                <div className="text-center border-2 border-green-400 p-4 bg-black">
                  <div className="text-lg text-green-300">WELCOME BACK,</div>
                  <div className="text-2xl font-bold text-green-400" style={{ textShadow: "0 0 10px #00ff41" }}>
                    {gameData.username.toUpperCase()}
                  </div>
                </div>
              )}
            </div>

            {/* Notification */}
            {showNotification && (
              <div
                className={`fixed top-4 right-4 px-6 py-3 border-2 font-mono z-50 ${
                  showNotification.type === "success"
                    ? "border-green-400 bg-black text-green-400"
                    : showNotification.type === "error"
                      ? "border-red-400 bg-black text-red-400"
                      : "border-cyan-400 bg-black text-cyan-400"
                }`}
                style={{
                  animation: "slideInRight 0.3s ease-out",
                  textShadow:
                    showNotification.type === "success"
                      ? "0 0 10px #00ff41"
                      : showNotification.type === "error"
                        ? "0 0 10px #ff0040"
                        : "0 0 10px #00ffff",
                }}
              >
                {showNotification.message}
              </div>
            )}
          </div>
        )

      case "gameModeSelect":
        return (
          <div className="min-h-screen bg-black text-green-400 p-8 font-mono">
            <div className="max-w-6xl mx-auto">
              <h2
                className="text-5xl font-bold text-center mb-4 text-cyan-400"
                style={{ textShadow: "0 0 20px #00ffff" }}
              >
                SELECT GAME MODE
              </h2>
              <p className="text-xl text-center text-green-300 mb-12 tracking-wider">
                &gt; CHOOSE YOUR BATTLE STYLE &lt;
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {Object.entries(GAME_MODES).map(([key, mode]) => (
                  <button
                    key={key}
                    onClick={() => {
                      saveGameData({ gameMode: key })
                      setGameState("characterSelect")
                    }}
                    className={`group relative p-6 border-2 transition-all duration-300 transform hover:scale-105 ${
                      gameData.gameMode === key
                        ? "border-cyan-400 bg-cyan-400/20"
                        : "border-green-400 bg-black hover:bg-green-400/20"
                    }`}
                  >
                    <div className="text-4xl mb-4">{mode.icon}</div>
                    <h3 className="text-2xl font-bold mb-2 text-green-400">{mode.name}</h3>
                    <p className="text-green-300 mb-4 text-sm">{mode.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-yellow-400 font-bold">+{mode.coins} COINS</span>
                      {gameData.gameMode === key && <span className="text-cyan-400 text-sm">SELECTED</span>}
                    </div>
                  </button>
                ))}
              </div>

              <div className="text-center">
                <button
                  onClick={() => setGameState("menu")}
                  className="px-8 py-3 bg-black border-2 border-green-400 text-green-400 hover:bg-green-400/20 transition-colors"
                >
                  &lt; BACK TO MENU
                </button>
              </div>
            </div>
          </div>
        )

      case "characterSelect":
        return (
          <div className="min-h-screen bg-black text-green-400 p-8 font-mono">
            <div className="max-w-6xl mx-auto">
              <h2
                className="text-5xl font-bold text-center mb-4 text-purple-400"
                style={{ textShadow: "0 0 20px #8000ff" }}
              >
                CHOOSE YOUR FIGHTER
              </h2>
              <p className="text-xl text-center text-green-300 mb-12 tracking-wider">&gt; SELECT YOUR CHAMPION &lt;</p>

              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-8">
                {Object.entries(CHARACTERS).map(([key, char]) => {
                  const isUnlocked = gameData.unlockedCharacters.includes(key)
                  const isSelected = selectedCharacters.player1 === key

                  return (
                    <button
                      key={key}
                      onClick={() => {
                        if (isUnlocked) {
                          setSelectedCharacters((prev) => ({ ...prev, player1: key }))
                          saveGameData({ selectedCharacter: key })
                        }
                      }}
                      disabled={!isUnlocked}
                      className={`group relative p-6 border-2 transition-all duration-300 transform hover:scale-105 ${
                        isSelected
                          ? "border-yellow-400 bg-yellow-400/20"
                          : isUnlocked
                            ? "border-green-400 bg-black hover:bg-green-400/20"
                            : "border-gray-600 bg-gray-900/50 opacity-50 cursor-not-allowed"
                      }`}
                    >
                      {!isUnlocked && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black/90 border-2 border-red-400">
                          <div className="text-center">
                            <div className="text-4xl mb-2">🔒</div>
                            <div className="text-sm text-red-400">LOCKED</div>
                          </div>
                        </div>
                      )}

                      {/* Character preview sprite */}
                      <div className="w-16 h-16 mx-auto mb-4 border-2 border-green-400 bg-black flex items-center justify-center">
                        <img
                          src={createCharacterPreviewSprite(char, 64).toDataURL() || "/placeholder.svg"}
                          alt={char.name}
                          className="w-full h-full pixelated"
                          style={{
                            imageRendering: "pixelated",
                            filter: isSelected ? `drop-shadow(0 0 8px ${char.color})` : "none",
                          }}
                        />
                      </div>

                      <h3 className="text-xl font-bold mb-2 text-green-400">{char.name}</h3>
                      <p className="text-sm text-green-300 mb-4">{char.description}</p>

                      <div className="text-xs space-y-1 font-mono">
                        <div className="flex justify-between">
                          <span>SPEED:</span>
                          <span className="text-cyan-400">{char.speed}★</span>
                        </div>
                        <div className="flex justify-between">
                          <span>JUMP:</span>
                          <span className="text-green-400">{char.jump_power}★</span>
                        </div>
                        <div className="flex justify-between">
                          <span>ATTACK:</span>
                          <span className="text-red-400">{char.attack_power}★</span>
                        </div>
                        <div className="flex justify-between">
                          <span>SPECIAL:</span>
                          <span className="text-purple-400">{char.special_power}★</span>
                        </div>
                      </div>

                      {char.rarity !== "common" && (
                        <div
                          className={`absolute top-2 right-2 px-2 py-1 border text-xs font-bold ${
                            char.rarity === "rare"
                              ? "border-blue-400 text-blue-400"
                              : char.rarity === "legendary"
                                ? "border-purple-400 text-purple-400"
                                : char.rarity === "mythic"
                                  ? "border-red-400 text-red-400"
                                  : "border-gray-400 text-gray-400"
                          }`}
                        >
                          {char.rarity.toUpperCase()}
                        </div>
                      )}

                      {isSelected && (
                        <div className="absolute -top-2 -right-2 w-6 h-6 bg-yellow-400 border-2 border-black flex items-center justify-center">
                          <span className="text-black text-xs">✓</span>
                        </div>
                      )}
                    </button>
                  )
                })}
              </div>

              {selectedCharacters.player1 && (
                <div className="text-center mb-8">
                  <div className="bg-black border-2 border-green-400 p-6 inline-block">
                    <h3 className="text-2xl font-bold mb-2 text-green-400">SELECTED FIGHTER</h3>
                    <div className="text-xl text-cyan-400">
                      {CHARACTERS[selectedCharacters.player1 as keyof typeof CHARACTERS].name}
                    </div>
                    <div className="text-sm text-green-300 mt-2">AI OPPONENT WILL BE RANDOMLY SELECTED</div>
                  </div>
                </div>
              )}

              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => setGameState("gameModeSelect")}
                  className="px-8 py-3 bg-black border-2 border-green-400 text-green-400 hover:bg-green-400/20 transition-colors"
                >
                  &lt; BACK
                </button>
                <button
                  onClick={() => {
                    if (selectedCharacters.player1) {
                      const availableChars = gameData.unlockedCharacters.filter((k) => k !== selectedCharacters.player1)
                      const aiChar = availableChars[Math.floor(Math.random() * availableChars.length)]
                      setSelectedCharacters((prev) => ({ ...prev, player2: aiChar }))
                      startGame()
                    }
                  }}
                  disabled={!selectedCharacters.player1}
                  className="px-8 py-3 bg-black border-2 border-red-400 text-red-400 hover:bg-red-400/20 disabled:border-gray-600 disabled:text-gray-600 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105"
                >
                  {gameData.gameMode === "online" ? "FIND MATCH 🌐" : "FIGHT! ⚔"}
                </button>
              </div>
            </div>
          </div>
        )

      case "shop":
        return (
          <div className="min-h-screen bg-black text-green-400 p-8 font-mono">
            <div className="max-w-6xl mx-auto">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-5xl font-bold text-green-400" style={{ textShadow: "0 0 20px #00ff41" }}>
                  ► SHOP
                </h2>
                <div className="bg-black border-2 border-yellow-400 p-4">
                  <div className="text-2xl font-bold text-yellow-400" style={{ textShadow: "0 0 10px #ffff00" }}>
                    {gameData.coins} COINS
                  </div>
                </div>
              </div>

              {/* Shop categories */}
              <div className="flex space-x-4 mb-8">
                {[
                  { key: "characters", label: "CHARACTERS", icon: "👤" },
                  { key: "emotes", label: "EMOTES", icon: "😄" },
                  { key: "superAttacks", label: "SUPER ATTACKS", icon: "💥" },
                ].map((category) => (
                  <button
                    key={category.key}
                    onClick={() => setShopCategory(category.key as any)}
                    className={`px-6 py-3 border-2 transition-all duration-300 ${
                      shopCategory === category.key
                        ? "border-green-400 bg-green-400/20 text-green-400"
                        : "border-gray-600 bg-black text-gray-400 hover:border-green-400 hover:text-green-400"
                    }`}
                  >
                    {category.icon} {category.label}
                  </button>
                ))}
              </div>

              {/* Shop items */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {shopCategory === "characters" &&
                  Object.entries(CHARACTERS).map(([key, char]) => {
                    const isUnlocked = gameData.unlockedCharacters.includes(key)

                    if (char.cost === 0) return null // Skip free characters

                    return (
                      <div key={key} className="bg-black border-2 border-green-400 p-6">
                        <div className="w-16 h-16 mx-auto mb-4 border-2 border-green-400 bg-black flex items-center justify-center">
                          <img
                            src={createCharacterPreviewSprite(char, 64).toDataURL() || "/placeholder.svg"}
                            alt={char.name}
                            className="w-full h-full pixelated"
                            style={{ imageRendering: "pixelated" }}
                          />
                        </div>
                        <h3 className="text-xl font-bold mb-2 text-center text-green-400">{char.name}</h3>
                        <p className="text-sm text-green-300 mb-4 text-center">{char.description}</p>

                        <div className="text-xs space-y-1 mb-4 font-mono">
                          <div className="flex justify-between">
                            <span>SPEED:</span>
                            <span className="text-cyan-400">{char.speed}★</span>
                          </div>
                          <div className="flex justify-between">
                            <span>ATTACK:</span>
                            <span className="text-red-400">{char.attack_power}★</span>
                          </div>
                          <div className="flex justify-between">
                            <span>SPECIAL:</span>
                            <span className="text-purple-400">{char.special_power}★</span>
                          </div>
                        </div>

                        {isUnlocked ? (
                          <div className="text-center text-green-400 font-bold border-2 border-green-400 py-2">
                            ✓ OWNED
                          </div>
                        ) : (
                          <button
                            onClick={() => purchaseItem("characters", key, char.cost)}
                            disabled={gameData.coins < char.cost}
                            className="w-full py-2 bg-black border-2 border-yellow-400 text-yellow-400 hover:bg-yellow-400/20 disabled:border-gray-600 disabled:text-gray-600 disabled:cursor-not-allowed transition-all duration-300"
                          >
                            BUY FOR {char.cost} COINS
                          </button>
                        )}
                      </div>
                    )
                  })}

                {shopCategory === "emotes" &&
                  Object.entries(EMOTES).map(([key, emote]) => {
                    const isUnlocked = gameData.unlockedEmotes.includes(key)

                    return (
                      <div key={key} className="bg-black border-2 border-green-400 p-6">
                        <div className="text-4xl text-center mb-4">{emote.icon}</div>
                        <h3 className="text-xl font-bold mb-2 text-center text-green-400">{emote.name}</h3>

                        {isUnlocked ? (
                          <div className="text-center text-green-400 font-bold border-2 border-green-400 py-2">
                            ✓ OWNED
                          </div>
                        ) : (
                          <button
                            onClick={() => purchaseItem("emotes", key, emote.cost)}
                            disabled={gameData.coins < emote.cost}
                            className="w-full py-2 bg-black border-2 border-yellow-400 text-yellow-400 hover:bg-yellow-400/20 disabled:border-gray-600 disabled:text-gray-600 disabled:cursor-not-allowed transition-all duration-300"
                          >
                            BUY FOR {emote.cost} COINS
                          </button>
                        )}
                      </div>
                    )
                  })}

                {shopCategory === "superAttacks" &&
                  Object.entries(SUPER_ATTACKS).map(([key, attack]) => {
                    const isUnlocked = gameData.unlockedSuperAttacks.includes(key)

                    return (
                      <div key={key} className="bg-black border-2 border-green-400 p-6">
                        <div className="text-4xl text-center mb-4">💥</div>
                        <h3 className="text-xl font-bold mb-2 text-center text-green-400">{attack.name}</h3>
                        <div className="text-center mb-4">
                          <span className="text-red-400 font-bold">DAMAGE: {attack.damage}★</span>
                        </div>

                        {isUnlocked ? (
                          <div className="text-center text-green-400 font-bold border-2 border-green-400 py-2">
                            ✓ OWNED
                          </div>
                        ) : (
                          <button
                            onClick={() => purchaseItem("superAttacks", key, attack.cost)}
                            disabled={gameData.coins < attack.cost}
                            className="w-full py-2 bg-black border-2 border-yellow-400 text-yellow-400 hover:bg-yellow-400/20 disabled:border-gray-600 disabled:text-gray-600 disabled:cursor-not-allowed transition-all duration-300"
                          >
                            BUY FOR {attack.cost} COINS
                          </button>
                        )}
                      </div>
                    )
                  })}
              </div>

              <div className="text-center">
                <button
                  onClick={() => setGameState("menu")}
                  className="px-8 py-3 bg-black border-2 border-green-400 text-green-400 hover:bg-green-400/20 transition-colors"
                >
                  &lt; BACK TO MENU
                </button>
              </div>
            </div>
          </div>
        )

      case "profile":
        return (
          <div className="min-h-screen bg-black text-green-400 p-8 font-mono">
            <div className="max-w-4xl mx-auto">
              <h2
                className="text-5xl font-bold text-center mb-8 text-cyan-400"
                style={{ textShadow: "0 0 20px #00ffff" }}
              >
                ► PLAYER PROFILE
              </h2>

              {/* Username input */}
              <div className="bg-black border-2 border-green-400 p-6 mb-8">
                <label className="block text-lg mb-2 text-green-400">USERNAME:</label>
                <input
                  type="text"
                  value={gameData.username}
                  onChange={(e) => saveGameData({ username: e.target.value })}
                  placeholder="ENTER YOUR USERNAME"
                  className="w-full px-4 py-2 bg-black border-2 border-green-400 text-green-400 font-mono placeholder-green-600 focus:outline-none focus:border-cyan-400"
                />
              </div>

              {/* Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-black border-2 border-yellow-400 p-6 text-center">
                  <div className="text-4xl font-bold text-yellow-400 mb-2" style={{ textShadow: "0 0 10px #ffff00" }}>
                    {gameData.coins}
                  </div>
                  <div className="text-lg text-yellow-300">TOTAL COINS</div>
                </div>
                <div className="bg-black border-2 border-green-400 p-6 text-center">
                  <div className="text-4xl font-bold text-green-400 mb-2" style={{ textShadow: "0 0 10px #00ff41" }}>
                    {gameData.totalWins}
                  </div>
                  <div className="text-lg text-green-300">TOTAL WINS</div>
                </div>
                <div className="bg-black border-2 border-cyan-400 p-6 text-center">
                  <div className="text-4xl font-bold text-cyan-400 mb-2" style={{ textShadow: "0 0 10px #00ffff" }}>
                    {gameData.totalMatches}
                  </div>
                  <div className="text-lg text-cyan-300">TOTAL MATCHES</div>
                </div>
              </div>

              {/* Win rate */}
              <div className="bg-black border-2 border-green-400 p-6 mb-8">
                <h3 className="text-2xl font-bold mb-4 text-green-400">PERFORMANCE</h3>
                <div className="flex items-center justify-between">
                  <span className="text-lg text-green-300">WIN RATE:</span>
                  <span className="text-2xl font-bold text-cyan-400">
                    {gameData.totalMatches > 0 ? Math.round((gameData.totalWins / gameData.totalMatches) * 100) : 0}%
                  </span>
                </div>
                <div className="w-full bg-gray-800 border-2 border-gray-600 h-4 mt-2">
                  <div
                    className="bg-cyan-400 h-full transition-all duration-500"
                    style={{
                      width: `${gameData.totalMatches > 0 ? (gameData.totalWins / gameData.totalMatches) * 100 : 0}%`,
                      boxShadow: "0 0 10px #00ffff",
                    }}
                  />
                </div>
              </div>

              {/* Unlocked content */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-black border-2 border-purple-400 p-6">
                  <h3 className="text-xl font-bold mb-4 text-purple-400">CHARACTERS</h3>
                  <div className="text-2xl font-bold text-purple-400 mb-2">
                    {gameData.unlockedCharacters.length}/{Object.keys(CHARACTERS).length}
                  </div>
                  <div className="text-sm text-purple-300">UNLOCKED</div>
                </div>
                <div className="bg-black border-2 border-yellow-400 p-6">
                  <h3 className="text-xl font-bold mb-4 text-yellow-400">EMOTES</h3>
                  <div className="text-2xl font-bold text-yellow-400 mb-2">
                    {gameData.unlockedEmotes.length}/{Object.keys(EMOTES).length}
                  </div>
                  <div className="text-sm text-yellow-300">UNLOCKED</div>
                </div>
                <div className="bg-black border-2 border-red-400 p-6">
                  <h3 className="text-xl font-bold mb-4 text-red-400">SUPER ATTACKS</h3>
                  <div className="text-2xl font-bold text-red-400 mb-2">
                    {gameData.unlockedSuperAttacks.length}/{Object.keys(SUPER_ATTACKS).length}
                  </div>
                  <div className="text-sm text-red-300">UNLOCKED</div>
                </div>
              </div>

              <div className="text-center">
                <button
                  onClick={() => setGameState("menu")}
                  className="px-8 py-3 bg-black border-2 border-green-400 text-green-400 hover:bg-green-400/20 transition-colors"
                >
                  &lt; BACK TO MENU
                </button>
              </div>
            </div>
          </div>
        )

      case "settings":
        return (
          <div className="min-h-screen bg-black text-green-400 p-8 font-mono">
            <div className="max-w-4xl mx-auto">
              <h2
                className="text-5xl font-bold text-center mb-8 text-yellow-400"
                style={{ textShadow: "0 0 20px #ffff00" }}
              >
                ► SETTINGS
              </h2>

              <div className="space-y-6">
                {/* Difficulty */}
                <div className="bg-black border-2 border-green-400 p-6">
                  <h3 className="text-2xl font-bold mb-4 text-green-400">DIFFICULTY</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {["Easy", "Normal", "Hard", "Insane"].map((diff) => (
                      <button
                        key={diff}
                        onClick={() => saveGameData({ settings: { ...gameData.settings, difficulty: diff } })}
                        className={`px-4 py-2 border-2 transition-all duration-300 ${
                          gameData.settings.difficulty === diff
                            ? diff === "Easy"
                              ? "border-green-400 bg-green-400/20 text-green-400"
                              : diff === "Normal"
                                ? "border-cyan-400 bg-cyan-400/20 text-cyan-400"
                                : diff === "Hard"
                                  ? "border-yellow-400 bg-yellow-400/20 text-yellow-400"
                                  : "border-red-400 bg-red-400/20 text-red-400"
                            : "border-gray-600 bg-black text-gray-400 hover:border-green-400 hover:text-green-400"
                        }`}
                      >
                        {diff.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Audio settings */}
                <div className="bg-black border-2 border-green-400 p-6">
                  <h3 className="text-2xl font-bold mb-4 text-green-400">AUDIO</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-lg text-green-300">SOUND EFFECTS</span>
                      <button
                        onClick={() =>
                          saveGameData({
                            settings: { ...gameData.settings, soundEnabled: !gameData.settings.soundEnabled },
                          })
                        }
                        className={`px-4 py-2 border-2 transition-all duration-300 ${
                          gameData.settings.soundEnabled
                            ? "border-green-400 bg-green-400/20 text-green-400"
                            : "border-red-400 bg-red-400/20 text-red-400"
                        }`}
                      >
                        {gameData.settings.soundEnabled ? "ON" : "OFF"}
                      </button>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-lg text-green-300">MUSIC</span>
                      <button
                        onClick={() =>
                          saveGameData({
                            settings: { ...gameData.settings, musicEnabled: !gameData.settings.musicEnabled },
                          })
                        }
                        className={`px-4 py-2 border-2 transition-all duration-300 ${
                          gameData.settings.musicEnabled
                            ? "border-green-400 bg-green-400/20 text-green-400"
                            : "border-red-400 bg-red-400/20 text-red-400"
                        }`}
                      >
                        {gameData.settings.musicEnabled ? "ON" : "OFF"}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Keybinds */}
                <div className="bg-black border-2 border-cyan-400 p-6">
                  <h3 className="text-2xl font-bold mb-4 text-cyan-400">KEYBINDS</h3>
                  <button
                    onClick={() => setGameState("keybinds")}
                    className="px-6 py-3 border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400/20 transition-colors"
                  >
                    CONFIGURE CONTROLS
                  </button>
                </div>

                {/* Reset data */}
                <div className="bg-black border-2 border-red-400 p-6">
                  <h3 className="text-2xl font-bold mb-4 text-red-400">DANGER ZONE</h3>
                  <p className="text-red-300 mb-4">RESET ALL GAME DATA INCLUDING COINS, UNLOCKS, AND PROGRESS.</p>
                  <button
                    onClick={() => {
                      if (confirm("ARE YOU SURE YOU WANT TO RESET ALL DATA? THIS CANNOT BE UNDONE!")) {
                        localStorage.removeItem("comboBros2D_gameData")
                        window.location.reload()
                      }
                    }}
                    className="px-6 py-3 border-2 border-red-400 text-red-400 hover:bg-red-400/20 transition-colors"
                  >
                    RESET ALL DATA
                  </button>
                </div>
              </div>

              <div className="text-center mt-8">
                <button
                  onClick={() => setGameState("menu")}
                  className="px-8 py-3 bg-black border-2 border-green-400 text-green-400 hover:bg-green-400/20 transition-colors"
                >
                  &lt; BACK TO MENU
                </button>
              </div>
            </div>
          </div>
        )

      case "keybinds":
        return (
          <div className="min-h-screen bg-black text-green-400 p-8 font-mono">
            <div className="max-w-4xl mx-auto">
              <h2
                className="text-5xl font-bold text-center mb-8 text-cyan-400"
                style={{ textShadow: "0 0 20px #00ffff" }}
              >
                ► KEYBINDS
              </h2>

              {bindingKey && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
                  <div className="bg-black border-4 border-yellow-400 p-8 text-center">
                    <h3 className="text-2xl font-bold mb-4 text-yellow-400">PRESS A KEY</h3>
                    <p className="text-green-300 mb-4">BINDING: {bindingKey.toUpperCase()}</p>
                    <button
                      onClick={() => setBindingKey(null)}
                      className="px-4 py-2 border-2 border-red-400 text-red-400 hover:bg-red-400/20"
                    >
                      CANCEL
                    </button>
                  </div>
                </div>
              )}

              <div className="bg-black border-2 border-green-400 p-6 mb-8">
                <h3 className="text-2xl font-bold mb-6 text-green-400">CONTROLS</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(gameData.keybinds).map(([action, key]) => (
                    <div key={action} className="flex items-center justify-between p-4 border border-green-400/30">
                      <span className="text-green-300 capitalize">
                        {action.replace(/([A-Z])/g, " $1").toUpperCase()}:
                      </span>
                      <button
                        onClick={() => setBindingKey(action)}
                        className="px-4 py-2 border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400/20 transition-colors min-w-[80px]"
                      >
                        {getKeyName(key)}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-black border-2 border-yellow-400 p-6 mb-8">
                <h3 className="text-2xl font-bold mb-4 text-yellow-400">DEFAULT CONTROLS</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                  <div className="text-green-300">MOVE: W/A/S/D</div>
                  <div className="text-green-300">ATTACK: F</div>
                  <div className="text-green-300">SPECIAL: G</div>
                  <div className="text-green-300">EMOTES: 1/2/3</div>
                </div>
                <button
                  onClick={() => saveGameData({ keybinds: DEFAULT_KEYBINDS })}
                  className="mt-4 px-6 py-2 border-2 border-yellow-400 text-yellow-400 hover:bg-yellow-400/20 transition-colors"
                >
                  RESET TO DEFAULT
                </button>
              </div>

              <div className="text-center">
                <button
                  onClick={() => setGameState("settings")}
                  className="px-8 py-3 bg-black border-2 border-green-400 text-green-400 hover:bg-green-400/20 transition-colors"
                >
                  &lt; BACK TO SETTINGS
                </button>
              </div>
            </div>
          </div>
        )

      case "game":
        return (
          <div className="flex flex-col items-center justify-center min-h-screen bg-black">
            <canvas
              ref={canvasRef}
              width={SCREEN_WIDTH}
              height={SCREEN_HEIGHT}
              className="border-2 border-green-400 shadow-2xl"
              style={{ boxShadow: "0 0 20px #00ff41" }}
            />
            <div className="mt-4 text-green-400 text-center bg-black border-2 border-green-400 p-4 font-mono">
              <p className="text-lg font-bold mb-2 text-green-400">► CONTROLS</p>
              <p className="text-sm">
                {getKeyName(gameData.keybinds.up)}/{getKeyName(gameData.keybinds.left)}/
                {getKeyName(gameData.keybinds.down)}/{getKeyName(gameData.keybinds.right)} - MOVE/JUMP |{" "}
                {getKeyName(gameData.keybinds.attack)} - ATTACK | {getKeyName(gameData.keybinds.special)} - SPECIAL
              </p>
              <p className="text-sm">
                {getKeyName(gameData.keybinds.emote1)}/{getKeyName(gameData.keybinds.emote2)}/
                {getKeyName(gameData.keybinds.emote3)} - EMOTES | ESC - RETURN TO MENU
              </p>
              <div className="mt-2 text-cyan-400">
                MODE: {GAME_MODES[gameData.gameMode as keyof typeof GAME_MODES]?.name} | DIFFICULTY:{" "}
                {gameData.settings.difficulty.toUpperCase()}
              </div>
            </div>
          </div>
        )

      case "gameOver":
        return (
          <div className="min-h-screen bg-black text-green-400 flex items-center justify-center font-mono">
            <div className="text-center border-4 border-green-400 p-12 bg-black">
              <h2 className="text-8xl font-bold mb-4 text-red-400" style={{ textShadow: "0 0 30px #ff0040" }}>
                GAME OVER
              </h2>
              <div className="text-4xl mb-8">
                {winner === "Draw" ? (
                  <span className="text-yellow-400">IT&apos;S A DRAW!</span>
                ) : (
                  <span className="text-green-400">{winner?.toUpperCase()} WINS!</span>
                )}
              </div>

              {/* Rewards */}
              <div className="bg-black border-2 border-yellow-400 p-6 mb-8 inline-block">
                <h3 className="text-2xl font-bold mb-4 text-yellow-400">MATCH REWARDS</h3>
                <div className="text-yellow-400 text-xl">
                  +
                  {winner !== "Draw" && winner === gameObjects.current.player1?.character_data.name
                    ? GAME_MODES[gameData.gameMode as keyof typeof GAME_MODES]?.coins || 50
                    : Math.floor((GAME_MODES[gameData.gameMode as keyof typeof GAME_MODES]?.coins || 50) / 2)}{" "}
                  COINS
                </div>
              </div>

              <div className="space-x-4">
                <button
                  onClick={() => {
                    setGameState("characterSelect")
                    setWinner(null)
                  }}
                  className="px-8 py-4 text-xl bg-black border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400/20 transition-all duration-300 transform hover:scale-105"
                >
                  ► PLAY AGAIN
                </button>
                <button
                  onClick={() => {
                    setGameState("menu")
                    setWinner(null)
                  }}
                  className="px-8 py-4 text-xl bg-black border-2 border-green-400 text-green-400 hover:bg-green-400/20 transition-all duration-300 transform hover:scale-105"
                >
                  ► MAIN MENU
                </button>
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  const [showUsernamePrompt, setShowUsernamePrompt] = useState(false)
  const [pendingUsername, setPendingUsername] = useState("")
  const [pendingPassword, setPendingPassword] = useState("")
  const [authMode, setAuthMode] = useState<'signup' | 'login'>("signup")
  const [authError, setAuthError] = useState("")
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // On mount, check if user is authenticated
  useEffect(() => {
    const savedData = localStorage.getItem("comboBros2D_gameData")
    const authFlag = localStorage.getItem("comboBros2D_isAuthenticated")
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData)
        if (parsed.username && parsed.password) {
          if (authFlag === "true") {
            setIsAuthenticated(true)
            setShowUsernamePrompt(false)
          } else {
            setAuthMode("login")
            setShowUsernamePrompt(true)
          }
        } else if (!parsed.username) {
          setAuthMode("signup")
          setShowUsernamePrompt(true)
        }
      } catch {
        setAuthMode("signup")
        setShowUsernamePrompt(true)
      }
    } else {
      setAuthMode("signup")
      setShowUsernamePrompt(true)
    }
  }, [])

  return (
    <div className="w-full h-screen">
      <div className="fixed top-4 right-4 z-50 flex items-center gap-2">
        {isAuthenticated && (
          <button
            className="ml-2 px-4 py-2 bg-red-400 text-black font-bold rounded hover:bg-red-500 border-2 border-red-400 transition"
            onClick={() => {
              localStorage.removeItem("comboBros2D_isAuthenticated")
              setIsAuthenticated(false)
              setShowUsernamePrompt(true)
              setAuthMode("login")
              setPendingUsername("")
              setPendingPassword("")
              setAuthError("")
            }}
          >
            LOGOUT
          </button>
        )}
      </div>
      {showUsernamePrompt && !isAuthenticated && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50">
          <div className="bg-black border-4 border-green-400 p-8 rounded-lg shadow-xl w-full max-w-md">
            <h2 className="text-3xl font-bold mb-4 text-green-400 text-center">
              {authMode === "signup" ? "WELCOME TO COMBO BROS 2D!" : "LOGIN"}
            </h2>
            <p className="text-green-300 mb-6 text-center">
              {authMode === "signup"
                ? "Please create a username and password to get started:"
                : "Enter your username and password to continue:"}
            </p>
            <input
              type="text"
              value={pendingUsername}
              onChange={e => setPendingUsername(e.target.value)}
              placeholder="Username"
              className="w-full px-4 py-2 mb-4 border-2 border-green-400 bg-black text-green-400 font-mono rounded focus:outline-none focus:border-cyan-400"
              maxLength={20}
              autoFocus
            />
            <input
              type="password"
              value={pendingPassword}
              onChange={e => setPendingPassword(e.target.value)}
              placeholder="Password"
              className="w-full px-4 py-2 mb-4 border-2 border-green-400 bg-black text-green-400 font-mono rounded focus:outline-none focus:border-cyan-400"
              maxLength={32}
            />
            {authError && <div className="text-red-400 mb-2 text-center">{authError}</div>}
            <button
              className="w-full py-2 bg-green-400 text-black font-bold rounded hover:bg-green-500 transition mb-2"
              disabled={!pendingUsername.trim() || !pendingPassword.trim()}
              onClick={() => {
                if (authMode === "signup") {
                  // Save username and password to localStorage
                  const newData = { ...gameData, username: pendingUsername.trim(), password: pendingPassword.trim() }
                  setGameData(newData)
                  localStorage.setItem("comboBros2D_gameData", JSON.stringify(newData))
                  localStorage.setItem("comboBros2D_isAuthenticated", "true")
                  setIsAuthenticated(true)
                  setShowUsernamePrompt(false)
                } else {
                  // Login: check credentials
                  const savedData = localStorage.getItem("comboBros2D_gameData")
                  if (savedData) {
                    try {
                      const parsed = JSON.parse(savedData)
                      if (
                        parsed.username === pendingUsername.trim() &&
                        parsed.password === pendingPassword.trim()
                      ) {
                        setGameData(parsed)
                        localStorage.setItem("comboBros2D_isAuthenticated", "true")
                        setIsAuthenticated(true)
                        setShowUsernamePrompt(false)
                        setAuthError("")
                      } else {
                        setAuthError("Invalid username or password.")
                      }
                    } catch {
                      setAuthError("Corrupted save data. Please sign up again.")
                      setAuthMode("signup")
                    }
                  } else {
                    setAuthError("No account found. Please sign up.")
                    setAuthMode("signup")
                  }
                }
              }}
            >
              {authMode === "signup" ? "SIGN UP" : "LOGIN"}
            </button>
            {authMode === "login" && (
              <button
                className="w-full py-2 bg-cyan-400 text-black font-bold rounded hover:bg-cyan-500 transition"
                onClick={() => {
                  setAuthMode("signup")
                  setPendingUsername("")
                  setPendingPassword("")
                  setAuthError("")
                }}
              >
                CREATE NEW ACCOUNT
              </button>
            )}
          </div>
        </div>
      )}
      {isAuthenticated && renderScreen()}
    </div>
  )
}
