class Suits
    :DIAMONDS
    :HEARTS
    :SPADES
    :CLUBS

    # Order these in increasing value
    @@all_suits = [
        :CLUBS,
        :SPADES,
        :HEARTS,
        :DIAMONDS,
    ]

    def self.all_suits
        @@all_suits
    end
end

class Card
    include Comparable

    @value = 1
    @suit = :HEARTS

    def <=>(another)
        (@value <=> another.value).nonzero? ||
        (Suits.all_suits.index(@suit) <=> Suits.all_suits.index(another.suit))
    end

    def initialize(value, suit)
        if !Suits.all_suits.include? suit
            raise "Invalid suit"
        end

        if !value.between?(1, 12)
            raise "Invalid value"
        end

        @value = value
        @suit = suit
    end

    def name
        return  case @value
                when 12
                    "King"
                when 11
                    "Queen"
                when 10
                    "Jack"
                when 1
                    "Ace"
                else
                    @value.to_s
                end
    end

    def to_s
        return "#{name} of #{@suit.to_s.capitalize}"
    end

    def value
        @value
    end

    def suit
        @suit
    end
end

class Deck
    @cards

    def initialize
        @cards = []
        for suit in Suits.all_suits
            for i in 1..12
                @cards.push(Card.new(i, suit))
            end
        end
    end

    def shuffle!
        @cards.shuffle!
    end

    def draw
        return @cards.shift
    end

    def print_cards
        for card in @cards
            puts card
        end
    end
end

class Player
    include Comparable

    @name = "Player"
    @hand = []

    def <=>(another)
        highest_card <=> another.highest_card
    end

    def initialize(name)
        @name = name
        @hand = []
    end

    def deal(card)
        if !card.is_a? Card
            raise "Invalid card"
        end

        @hand.push(card)
    end

    def highest_card
        @hand.sort!.reverse![0]
    end

    def print_hand
        for card in @hand
            puts card
        end
    end

    def name
        @name
    end
end

class Game
    @deck
    @players
    @started = false

    def initialize
        @deck = Deck.new
        @players = []
        @started = false
    end

    def start
        n = 0
        loop do
            puts "Enter number of players:"
            n = gets.to_i
            break if n.between?(2,5)
            puts "Only 2-5 players are allowed"
        end
        puts "Starting game...\n"
        for i in 1..n
            puts "Enter name for player #{i}:"
            name = gets.chomp
            @players.push(Player.new(name.empty? ? "Player #{i}" : name))
        end

        puts "Shuffling deck...\n"
        @deck.shuffle!

        for i in 1..3
            for player in @players
                player.deal(@deck.draw)
            end
        end

        for player in @players
            puts "#{player.name} has"
            player.print_hand
            puts ''
        end

        @players.sort!.reverse!
        @started = true
    end

    def winner
        if !@started
            raise "Game has not started"
        end

        winner = @players[0]
        puts "#{winner.name} wins with card #{winner.highest_card}!"
    end
end

game = Game.new
game.start
game.winner
